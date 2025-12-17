from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.schemas.lead import LeadAnalytics
from app.services.lead_service import get_leads_with_analytics, get_all_leads
from app.services.persona_insight_service import generate_all_persona_insights
from app.services.alert_service import generate_alerts
from app.services.trust_service import calculate_data_freshness
from app.services.data_quality_service import analyze_data_quality

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/risk_profile", response_model=List[LeadAnalytics])
def get_lead_risk_profile(db: Session = Depends(get_db)):
    """
    Retrieves all leads with their calculated risk, SLA, and trust analytics.
    """
    analytics_data = get_leads_with_analytics(db)
    return analytics_data

@router.get("/data_freshness", response_model=Dict[str, Any])
def get_data_freshness(db: Session = Depends(get_db)):
    """
    Calculates and returns the data freshness score for the entire dataset.
    """
    leads = get_all_leads(db)
    freshness_data = calculate_data_freshness(leads)
    return freshness_data

@router.get("/data_quality", response_model=Dict[str, Any])
def get_data_quality(db: Session = Depends(get_db)):
    """
    Analyzes the overall data quality and returns a confidence score.
    """
    leads = get_all_leads(db)
    quality_report = analyze_data_quality(leads)
    return quality_report

@router.get("/persona_insights", response_model=str)
def get_persona_insights(persona: str, db: Session = Depends(get_db)):
    """
    Generates and returns a persona-specific insight string.
    """
    analytics_data = get_leads_with_analytics(db)
    insights = generate_all_persona_insights(db, analytics_data)
    persona_map = {
        "founder": "Founder",
        "sales": "Sales Manager",
        "ops": "Operations Manager"
    }
    insight_key = persona_map.get(persona.lower())
    if not insight_key or insight_key not in insights:
        raise HTTPException(status_code=404, detail=f"Persona '{persona}' not found.")
    return insights[insight_key]

@router.get("/alerts", response_model=List[Dict[str, Any]])
def get_alerts(persona: str, db: Session = Depends(get_db)):
    """
    Generates and returns a list of proactive alerts based on persona.
    """
    analytics_data = get_leads_with_analytics(db)
    persona_key = persona.lower()
    if persona_key not in ["founder", "sales", "ops"]:
        raise HTTPException(status_code=400, detail="Invalid persona specified.")
    
    alerts = generate_alerts(db, analytics_data, persona_key)
    return alerts
