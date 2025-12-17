from datetime import datetime, timezone
from typing import List, Dict, Any
import logging
from app.models.lead import Lead

# --- Constants ---
SLA_THRESHOLDS = {"new": 3, "contacted": 7, "qualified": 14}
RISK_SCORE_WEIGHTS = {
    "sla_breach": 40,
    "age_multiplier": 1.5,
    "age_max_score": 30,
    "low_followup_penalty": 20,
    "source_penalty": {"organic": 0, "referral": -5, "manual": 10, "ads": 15}
}

def get_lead_age_days(lead: Lead) -> int:
    """Safely calculates the age of a lead in days."""
    if not lead or not lead.created_at:
        return 0
    # Ensure created_at is offset-aware for correct calculations
    created_at = lead.created_at.replace(tzinfo=timezone.utc) if lead.created_at.tzinfo is None else lead.created_at
    return (datetime.now(timezone.utc) - created_at).days

def is_sla_breached(age_days: int, status: str) -> bool:
    """Checks if a lead's age exceeds the SLA for its status."""
    return age_days > SLA_THRESHOLDS.get(status, float('inf'))

def calculate_risk_score(age_days: int, status: str, source: str, followup_count: int) -> Dict[str, Any]:
    """
    Calculates a risk score for a lead based on multiple factors.
    Returns a dictionary with the score and level.
    """
    try:
        score = 0
        # 1. SLA Breach
        if is_sla_breached(age_days, status):
            score += RISK_SCORE_WEIGHTS.get("sla_breach", 0)
        # 2. Lead Age
        age_score = min(age_days * RISK_SCORE_WEIGHTS.get("age_multiplier", 0), RISK_SCORE_WEIGHTS.get("age_max_score", 0))
        score += age_score
        # 3. Low Engagement
        if followup_count <= 1:
            score += RISK_SCORE_WEIGHTS.get("low_followup_penalty", 0)
        # 4. Source
        score += RISK_SCORE_WEIGHTS.get("source_penalty", {}).get(source, 0)
        
        final_score = max(0, min(100, int(score)))

        if final_score > 75:
            level = "High"
        elif final_score > 40:
            level = "Medium"
        else:
            level = "Low"
            
        return {"score": final_score, "level": level}
    except Exception as e:
        logging.error(f"Error in calculate_risk_score: {e}")
        return {"score": -1, "level": "Error"}

def process_lead_analytics(leads: List[Lead]) -> List[Dict[str, Any]]:
    """
    Processes a list of leads and returns their analytics data.
    Handles empty or invalid input gracefully.
    """
    if not leads:
        return [{"data_status": "empty"}]

    analytics_results = []
    for lead in leads:
        try:
            if not isinstance(lead, Lead): continue

            age_days = get_lead_age_days(lead)
            followup_count = len(lead.followups) if lead.followups else 0
            risk = calculate_risk_score(age_days, lead.status, lead.source, followup_count)

            analytics_results.append({
                "id": lead.id,
                "name": getattr(lead, 'name', 'Unknown'),
                "status": getattr(lead, 'status', 'unknown'),
                "source": getattr(lead, 'source', 'unknown'),
                "age_days": age_days,
                "sla_breached": is_sla_breached(age_days, getattr(lead, 'status', 'unknown')),
                "risk_score": risk["score"],
                "risk_level": risk["level"],
                "followup_count": followup_count,
            })
        except Exception as e:
            logging.error(f"Failed to process analytics for lead ID {getattr(lead, 'id', 'N/A')}: {e}")
            # Optionally, append a record indicating failure for this lead
            analytics_results.append({
                "id": getattr(lead, 'id', 'N/A'),
                "name": "Processing Error",
                "risk_level": "Error",
                "data_status": "error"
            })
            
    return analytics_results
