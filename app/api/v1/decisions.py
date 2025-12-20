from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.schemas.decision import DecisionRecommendation
from app.schemas.decision_proposal import DecisionProposalCreate, DecisionProposalOut
from app.schemas.decision_review import DecisionReview
from app.schemas.override import DecisionOverride
from app.core.decision.engine import generate_recommendations, filter_recommendations_by_persona, explain_decision, PERSONA_WEIGHTS
from app.services.decision_service import create_decision_proposal, override_decision
from app.services.decision_review_service import review_decision
from app.core.decision.confidence import get_system_confidence
from app.services.analytics_service import get_key_metrics
from app.core.governance.audit import create_audit_log_entry
from app.schemas.audit_log import AuditLogCreate
from app.core.auth.security import get_current_user_role, UserRole, require_roles, UserContext, get_current_user
from app.services.decision_sla_service import evaluate_decision_sla
from app.models.decision_feedback import DecisionFeedback
from app.schemas.decision_feedback import DecisionFeedbackCreate, DecisionFeedbackRead
from app.services.traceability_service import capture_decision_snapshot, get_decision_snapshot
from app.schemas.decision_snapshot import DecisionSnapshotRead

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)

@router.get("/recommendations", response_model=List[DecisionRecommendation])
def get_decision_recommendations(
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role),
    user: UserContext = Depends(get_current_user)
):
    """
    Generates and filters actionable recommendations based on the user's persona.
    """
    try:
        confidence_data = get_system_confidence(db)
        analytics_metrics = get_key_metrics(db)
        
        # Pass persona to generate_recommendations for weighting
        all_recommendations = generate_recommendations(
            analytics_metrics=analytics_metrics,
            confidence_score=confidence_data.score,
            persona=role
        )
        
        filtered_recommendations = filter_recommendations_by_persona(all_recommendations, role)
        
        final_recommendations = []
        for rec in filtered_recommendations:
            # Capture snapshot for traceability
            snapshot = capture_decision_snapshot(
                db=db,
                decision=rec,
                user_id=user.user_id,
                persona=role,
                inputs=analytics_metrics,
                rules_fired=rec.explanation.get("triggered_rule_ids", []) if rec.explanation else [],
                weights={"persona_weight": PERSONA_WEIGHTS.get(role, 1.0)},
                model_version="v1.0"
            )
            
            # Update recommendation ID with the generated DTID
            rec.id = snapshot.decision_id
            
            log_details = json.dumps({
                "title": rec.title,
                "priority": rec.priority.value,
                "confidence": rec.confidence,
                "explanation": rec.explanation,
                "dtid": snapshot.decision_id
            })
            
            log_entry = AuditLogCreate(
                event_type="decision_generated",
                decision=rec.recommendation[:255],
                details=log_details,
                persona=role.value if role else "anonymous"
            )
            create_audit_log_entry(db, log_entry)
            final_recommendations.append(rec)
        
        return final_recommendations

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.get("/{decision_id}", response_model=DecisionSnapshotRead)
def get_decision_trace(
    decision_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves the full snapshot and trace for a specific decision ID (DTID).
    """
    snapshot = get_decision_snapshot(db, decision_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Decision trace not found")
    return snapshot

@router.post("/feedback", response_model=DecisionFeedbackRead, status_code=status.HTTP_201_CREATED)
def submit_decision_feedback(
    feedback: DecisionFeedbackCreate,
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role)
):
    """
    Records human feedback on a decision recommendation.
    """
    try:
        db_feedback = DecisionFeedback(
            recommendation_id=feedback.recommendation_id,
            recommendation_title=feedback.recommendation_title,
            persona=role.value if role else "anonymous",
            decision=feedback.decision.value,
            reason=feedback.reason
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        # Audit Log
        log_details = json.dumps({
            "recommendation_id": feedback.recommendation_id,
            "recommendation_title": feedback.recommendation_title,
            "decision": feedback.decision.value,
            "reason": feedback.reason
        })
        
        audit_entry = AuditLogCreate(
            event_type="decision_feedback",
            decision=feedback.decision.value,
            details=log_details,
            persona=role.value if role else "anonymous"
        )
        create_audit_log_entry(db, audit_entry)

        return db_feedback

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )

@router.post("", response_model=DecisionProposalOut, status_code=status.HTTP_201_CREATED)
def submit_decision_proposal(payload: DecisionProposalCreate, db: Session = Depends(get_db)):
    return create_decision_proposal(db, payload)

@router.post("/{proposal_id}/review", response_model=DecisionProposalOut)
def review_decision_api(
    proposal_id: int,
    payload: DecisionReview,
    db: Session = Depends(get_db)
):
    return review_decision(db, proposal_id, payload)

@router.post("/{proposal_id}/override", response_model=DecisionProposalOut, dependencies=[Depends(require_roles([UserRole.FOUNDER, UserRole.OPS_CRM]))])
def override_decision_api(
    proposal_id: int,
    new_decision: str,
    override_reason: str,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    override_data = DecisionOverride(
        by=user.user_id,
        role=user.role.value,
        reason=override_reason
    )
    
    overridden_proposal = override_decision(db, proposal_id, new_decision, override_data)

    # Audit the override event
    log_details = json.dumps({
        "proposal_id": proposal_id,
        "original_decision": overridden_proposal.original_recommendation,
        "new_decision": new_decision,
        "reason": override_reason,
        "overridden_by": user.user_id
    })
    log_entry = AuditLogCreate(
        event_type="decision_override",
        decision="OVERRIDDEN",
        details=log_details,
        persona=user.role.value
    )
    create_audit_log_entry(db, log_entry)

    return overridden_proposal

@router.post("/sla/evaluate")
def evaluate_sla_endpoint(db: Session = Depends(get_db)):
    count = evaluate_decision_sla(db)
    return {"escalated": count}
