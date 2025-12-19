from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.schemas.decision import DecisionRecommendation
from app.schemas.decision_proposal import DecisionProposalCreate, DecisionProposalOut
from app.schemas.decision_review import DecisionReview
from app.schemas.override import DecisionOverride
from app.services.decision_engine import generate_recommendations, filter_recommendations_by_persona, explain_decision
from app.services.decision_service import create_decision_proposal, override_decision
from app.services.decision_review_service import review_decision
from app.services.confidence_service import get_system_confidence
from app.services.analytics_service import get_key_metrics
from app.services.audit_log_service import create_audit_log_entry
from app.schemas.audit_log import AuditLogCreate
from app.core.security import get_current_user_role, UserRole, require_roles, UserContext, get_current_user
from app.services.decision_sla_service import evaluate_decision_sla

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)

@router.get("/recommendations", response_model=List[DecisionRecommendation])
def get_decision_recommendations(
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role)
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
        
        for rec in filtered_recommendations:
            log_details = json.dumps({
                "title": rec.title,
                "priority": rec.priority.value,
                "confidence": rec.confidence,
                "explanation": rec.explanation
            })
            
            log_entry = AuditLogCreate(
                event_type="decision_generated",
                decision=rec.recommendation[:255],
                details=log_details,
                persona=role.value if role else "anonymous"
            )
            create_audit_log_entry(db, log_entry)
        
        return filtered_recommendations

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
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
