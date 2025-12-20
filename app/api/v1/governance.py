from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.audit_log import AuditLog
from app.core.governance.audit import get_audit_logs
from app.core.cache import clear_cache
from app.core.auth.security import require_roles, UserRole

router = APIRouter(
    prefix="/governance",
    tags=["Governance"],
    dependencies=[Depends(require_roles([UserRole.FOUNDER]))]
)

@router.get("/audit_logs", response_model=List[AuditLog])
def read_audit_logs(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    persona: Optional[str] = Query(None, description="Filter by persona"),
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve audit logs for governance and traceability, with optional filters.
    """
    return get_audit_logs(
        db=db,
        event_type=event_type,
        persona=persona,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

@router.post("/cache/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_system_cache():
    """
    Manually invalidates and clears the entire in-memory cache for all services.
    """
    clear_cache()
    return
