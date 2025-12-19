from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List

from app.core.database import get_db
from app.core.security import get_current_user_role, UserRole
from app.models.decision_feedback import DecisionFeedback, DecisionFeedbackType

router = APIRouter(
    prefix="/learning",
    tags=["Learning"]
)

@router.get("/insights")
def get_learning_insights(
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role)
):
    """
    Returns READ-ONLY insights derived from human feedback.
    """
    try:
        # 1. Rejection Rate
        total_decisions = db.query(func.count(DecisionFeedback.id)).scalar()
        rejected_decisions = db.query(func.count(DecisionFeedback.id)).filter(
            DecisionFeedback.decision == DecisionFeedbackType.REJECTED.value
        ).scalar()
        
        rejection_rate = 0.0
        if total_decisions > 0:
            rejection_rate = (rejected_decisions / total_decisions) * 100

        # 2. Persona Bias Detection
        # Check if any persona rejects > 65% of their decisions
        personas = db.query(DecisionFeedback.persona).distinct().all()
        persona_bias_detected = False
        biased_personas = []

        for p in personas:
            persona_name = p[0]
            p_total = db.query(func.count(DecisionFeedback.id)).filter(
                DecisionFeedback.persona == persona_name
            ).scalar()
            p_rejected = db.query(func.count(DecisionFeedback.id)).filter(
                DecisionFeedback.persona == persona_name,
                DecisionFeedback.decision == DecisionFeedbackType.REJECTED.value
            ).scalar()
            
            if p_total > 0:
                rate = (p_rejected / p_total)
                if rate > 0.65:
                    persona_bias_detected = True
                    biased_personas.append(persona_name)

        # 3. Confidence Drift
        # Based on rejection rate
        confidence_drift = "low"
        if rejection_rate > 50:
            confidence_drift = "high"
        elif rejection_rate > 20:
            confidence_drift = "medium"

        return {
            "rejection_rate": round(rejection_rate, 2),
            "total_decisions": total_decisions,
            "persona_bias_detected": persona_bias_detected,
            "biased_personas": biased_personas,
            "confidence_drift": confidence_drift
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve insights: {str(e)}"
        )
