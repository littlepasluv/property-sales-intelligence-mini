from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.audit_log import AuditLog
from app.services.audit_log_service import get_audit_logs

router = APIRouter(
    prefix="/governance",
    tags=["Governance"]
)

@router.get("/audit_logs", response_model=List[AuditLog])
def read_audit_logs(
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g., 'risk_calculation')."),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID."),
    persona: Optional[str] = Query(None, description="Filter by persona."),
    start_date: Optional[datetime] = Query(None, description="Start of date range (ISO 8601 format)."),
    end_date: Optional[datetime] = Query(None, description="End of date range (ISO 8601 format)."),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve audit logs for governance and traceability, with optional filters.
    """
    logs = get_audit_logs(
        db=db,
        event_type=event_type,
        entity_id=entity_id,
        persona=persona,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return logs
