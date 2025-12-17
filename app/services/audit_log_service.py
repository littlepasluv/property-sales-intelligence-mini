from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
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
    entity_id: Optional[int] = None,
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
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if persona:
        query = query.filter(AuditLog.persona == persona)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

# --- Helper functions for specific events ---

def log_risk_calculation(
    db: Session,
    lead_id: int,
    inputs: Dict[str, Any],
    decision: Dict[str, Any],
    confidence: float,
    explanation: str
):
    """Logs a risk score calculation event."""
    event = AuditLogCreate(
        event_type="risk_calculation",
        entity_type="lead",
        entity_id=lead_id,
        inputs=inputs,
        decision=decision,
        confidence=confidence,
        explainability_ref=explanation
    )
    create_audit_log_entry(db, event)

def log_sla_breach_detection(db: Session, lead_id: int, inputs: Dict[str, Any], decision: Dict[str, Any]):
    """Logs an SLA breach detection event."""
    event = AuditLogCreate(
        event_type="sla_breach_detection",
        entity_type="lead",
        entity_id=lead_id,
        inputs=inputs,
        decision=decision
    )
    create_audit_log_entry(db, event)

def log_persona_insight_generation(db: Session, persona: str, inputs: Dict[str, Any], decision: Dict[str, Any]):
    """Logs a persona insight generation event."""
    event = AuditLogCreate(
        event_type="persona_insight_generation",
        entity_type="persona_insight",
        persona=persona,
        inputs=inputs,
        decision=decision
    )
    create_audit_log_entry(db, event)

def log_alert_creation(db: Session, persona: str, inputs: Dict[str, Any], alerts: List[Dict[str, Any]]):
    """Logs an alert creation event."""
    for alert in alerts:
        event = AuditLogCreate(
            event_type="alert_creation",
            entity_type="alert",
            persona=persona,
            inputs=inputs,
            decision=alert
        )
        create_audit_log_entry(db, event)
