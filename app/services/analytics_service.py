from datetime import datetime, timezone
from typing import List
from app.models.lead import Lead

# --- Constants for SLA and Risk Calculation ---

SLA_THRESHOLDS = {
    "new": 2,
    "contacted": 3,
    "qualified": 5,
}

RISK_SCORE_WEIGHTS = {
    "sla_breach": 40,
    "age_multiplier": 5,
    "age_max_score": 30,
    "low_followup_penalty": 20,
    "source_penalty": {
        "Facebook Ads": 10
    }
}

# --- Pure Functions for Analytics Logic ---

def get_lead_age_days(lead: Lead) -> int:
    """Calculates the age of a lead in days."""
    return (datetime.now(timezone.utc) - lead.created_at.replace(tzinfo=timezone.utc)).days

def is_sla_breached(lead_age: int, status: str) -> bool:
    """Determines if a lead has breached its SLA for its current status."""
    return lead_age > SLA_THRESHOLDS.get(status, float('inf'))

def calculate_risk_score(lead_age: int, sla_breached: bool, followup_count: int, source: str) -> int:
    """
    Calculates a risk score for a lead based on several factors.
    The score is capped at 100.
    """
    score = 0
    if sla_breached:
        score += RISK_SCORE_WEIGHTS["sla_breach"]
    
    # Add score based on age, capped at a max value
    age_score = min(lead_age * RISK_SCORE_WEIGHTS["age_multiplier"], RISK_SCORE_WEIGHTS["age_max_score"])
    score += age_score
    
    # Penalize leads with few follow-ups
    if followup_count <= 1:
        score += RISK_SCORE_WEIGHTS["low_followup_penalty"]
        
    # Add penalty for specific sources
    score += RISK_SCORE_WEIGHTS["source_penalty"].get(source, 0)
    
    return min(score, 100)

def get_risk_level(risk_score: int) -> str:
    """Categorizes the risk score into Low, Medium, or High."""
    if risk_score >= 70:
        return "High"
    elif risk_score >= 40:
        return "Medium"
    else:
        return "Low"

def process_lead_analytics(leads: List[Lead]) -> List[dict]:
    """
    Processes a list of Lead models and returns a list of dictionaries
    with calculated analytics fields.
    """
    analytics_data = []
    for lead in leads:
        age_days = get_lead_age_days(lead)
        sla_breached = is_sla_breached(age_days, lead.status)
        followup_count = len(lead.followups)
        risk_score = calculate_risk_score(age_days, sla_breached, followup_count, lead.source)
        risk_level = get_risk_level(risk_score)
        
        analytics_data.append({
            "id": lead.id,
            "name": lead.name,
            "status": lead.status,
            "source": lead.source,
            "age_days": age_days,
            "sla_breached": sla_breached,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "followup_count": followup_count,
        })
    return analytics_data
