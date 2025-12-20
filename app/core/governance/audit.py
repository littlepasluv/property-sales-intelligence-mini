from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate
from app.core.cache import simple_cache, clear_cache

def create_audit_log_entry(db: Session, event: AuditLogCreate) -> AuditLog:
    """
    Creates and saves a new audit log entry.
    This is the central function for all governance logging.
    """
    db_log = AuditLog(**event.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    clear_cache() # Invalidate cache whenever a new log is created
    return db_log

@simple_cache(ttl=60)
def get_audit_logs(
    db: Session,
    event_type: Optional[str] = None,
    persona: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    """
    Retrieves audit logs with optional filtering. This function is cached.
    """
    query = db.query(AuditLog)

    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if persona:
        query = query.filter(AuditLog.persona == persona)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
