from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.decision import DecisionRecommendation
from app.services.decision_engine import calculate_risk_score, generate_recommendations, filter_recommendations_by_persona
from app.services.confidence_service import get_system_confidence
from app.services.analytics_service import get_key_metrics
from app.services.audit_log_service import create_audit_log_entry
from app.schemas.audit_log import AuditLogCreate
from app.core.security import get_current_user_role, UserRole

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
        # 1. Fetch Context Data
        confidence_data = get_system_confidence(db)
        analytics_metrics = get_key_metrics(db)
        
        # 2. Calculate Risk Score
        risk_score = calculate_risk_score(analytics_metrics)

        # 3. Generate All Possible Recommendations
        all_recommendations = generate_recommendations(
            risk_score=risk_score,
            confidence=confidence_data.score,
            completeness=analytics_metrics.get("data_completeness", 0)
        )
        
        # 4. Filter Recommendations by Persona
        filtered_recommendations = filter_recommendations_by_persona(all_recommendations, role)
        
        # 5. Audit the Decision Generation Event
        log_entry = AuditLogCreate(
            event_type="decision_generated",
            decision="advisory",
            details=f"Generated {len(all_recommendations)} total recommendations, returned {len(filtered_recommendations)} for persona.",
            persona=role.value if role else "anonymous"
        )
        create_audit_log_entry(db, log_entry)
        
        return filtered_recommendations

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
