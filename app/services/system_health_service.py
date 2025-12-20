from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from app.core.cache import simple_cache

def get_system_health(db: Session, last_ingestion_summary: Dict[str, Any]) -> Dict[str, Any]:
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return {
        "api": "healthy",
        "database": db_status,
        "ingestion": "healthy" if last_ingestion_summary else "unknown"
    }

def get_system_metrics(db: Session, last_ingestion_summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "total_leads": 100, # Dummy
        "active_users": 5,
        "last_ingestion": last_ingestion_summary
    }

def get_ingestion_status(last_ingestion_summary: Dict[str, Any]) -> Dict[str, Any]:
    return last_ingestion_summary or {"status": "no_run_yet"}

def get_full_system_health(db: Session) -> Dict[str, Any]:
    return get_system_health(db, {})
