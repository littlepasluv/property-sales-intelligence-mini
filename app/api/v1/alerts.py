from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import (
    alert_service,
    data_quality_service,
    insight_quality_service,
    trust_service
)
from app.services.lead_service import get_all_leads
from app.ingestion.registry import registry
from app.core.security import require_roles, UserRole

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
    dependencies=[Depends(require_roles([UserRole.FOUNDER, UserRole.OPS_CRM]))]
)

@router.get("/", response_model=Dict[str, Any])
def get_active_alerts(db: Session = Depends(get_db)):
    """
    Evaluates all alert rules and returns a list of currently active alerts.
    """
    # 1. Gather all necessary state from other services
    leads = get_all_leads(db)
    
    ingestion_status = registry.last_summary or {} 
    
    data_quality = data_quality_service.analyze_data_quality(leads)
    
    data_freshness = trust_service.calculate_data_freshness(leads)

    insight_quality = insight_quality_service.calculate_insight_quality(leads)

    # 2. Evaluate alerts
    active_alerts = alert_service.evaluate_alerts(
        ingestion_status,
        data_quality,
        data_freshness,
        insight_quality
    )
    
    # 3. Determine highest severity
    highest_severity = "none"
    if active_alerts:
        severities = [a["severity"] for a in active_alerts]
        if "high" in severities:
            highest_severity = "high"
        elif "medium" in severities:
            highest_severity = "medium"
        else:
            highest_severity = "low"

    return {
        "active_alerts": active_alerts,
        "alert_count": len(active_alerts),
        "highest_severity": highest_severity
    }
