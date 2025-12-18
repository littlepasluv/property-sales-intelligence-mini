from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.core.database import get_db
from app.schemas.confidence import ConfidenceScore, ConfidenceSignal
from app.schemas.audit_log import AuditLogCreate
from app.services.confidence_service import get_system_confidence
from app.services.audit_log_service import create_audit_log_entry
from app.core.security import UserRole, require_roles, get_current_user_role

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(require_roles([UserRole.FOUNDER, UserRole.SALES_MANAGER, UserRole.OPS_CRM, UserRole.VIEWER]))]
)

@router.get("/confidence", response_model=ConfidenceScore)
def get_confidence_endpoint(
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role)
):
    """
    Calculates and returns the system's overall confidence score.
    """
    try:
        confidence_data = get_system_confidence(db)
        
        log_details = (
            f"Score: {confidence_data.score}. "
            f"Guidance: '{confidence_data.decision_guidance}'. "
            f"Summary: {confidence_data.explanation_summary}"
        )
        
        log_entry = AuditLogCreate(
            event_type="confidence_evaluated",
            decision=confidence_data.level,
            details=log_details,
            persona=role.value if role else "anonymous"
        )
        create_audit_log_entry(db, log_entry)
        
        return confidence_data
    except Exception as e:
        logging.error(f"Error in get_confidence_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while calculating confidence.")

@router.get("/confidence/drivers", response_model=List[ConfidenceSignal])
def get_confidence_drivers_endpoint(db: Session = Depends(get_db)):
    """
    Returns a breakdown of the signals driving the system confidence score.
    """
    confidence_data = get_system_confidence(db)
    return confidence_data.signals
