from datetime import datetime, timezone
from typing import List, Dict, Any
from app.models.lead import Lead
from app.models.followup import Followup
from app.services.analytics_service import (
    SLA_THRESHOLDS,
    RISK_SCORE_WEIGHTS,
    get_lead_age_days,
    is_sla_breached,
)

def explain_lead_risk(lead: Lead, followups: List[Followup]) -> Dict[str, Any]:
    """
    Analyzes a single lead and breaks down its risk score into explainable factors.

    This function uses deterministic, rule-based logic to provide a transparent
    explanation of why a lead is considered high-risk. It is designed to be
    safe for executive viewing and provide actionable insights for sales teams.

    Args:
        lead: The SQLAlchemy Lead object.
        followups: A list of SQLAlchemy Followup objects associated with the lead.

    Returns:
        A dictionary containing the risk score breakdown, a summary explanation,
        and a recommended action.
    """
    risk_factors = []
    total_score = 0
    
    lead_age = get_lead_age_days(lead)
    followup_count = len(followups)
    sla_breached_flag = is_sla_breached(lead_age, lead.status)

    # 1. SLA Breach Factor
    if sla_breached_flag:
        weight = RISK_SCORE_WEIGHTS["sla_breach"]
        total_score += weight
        risk_factors.append({
            "type": "sla_breach",
            "weight": weight,
            "detail": f"Lead has been in the '{lead.status}' stage for {lead_age} days, exceeding the {SLA_THRESHOLDS.get(lead.status, 'N/A')}-day SLA."
        })

    # 2. Lead Age / Stagnation Factor
    age_score = min(lead_age * RISK_SCORE_WEIGHTS["age_multiplier"], RISK_SCORE_WEIGHTS["age_max_score"])
    if age_score > 0:
        total_score += age_score
        risk_factors.append({
            "type": "stage_stagnation",
            "weight": age_score,
            "detail": f"Lead is {lead_age} days old, indicating slow movement through the pipeline."
        })

    # 3. Low Engagement Factor
    if followup_count <= 1:
        weight = RISK_SCORE_WEIGHTS["low_followup_penalty"]
        total_score += weight
        risk_factors.append({
            "type": "low_engagement",
            "weight": weight,
            "detail": f"Only {followup_count} follow-up(s) have been logged, suggesting minimal engagement."
        })

    # 4. Source-based Risk Factor
    source_penalty = RISK_SCORE_WEIGHTS["source_penalty"].get(lead.source, 0)
    if source_penalty > 0:
        total_score += source_penalty
        risk_factors.append({
            "type": "source_risk",
            "weight": source_penalty,
            "detail": f"Leads from '{lead.source}' are considered higher risk based on historical performance."
        })

    # Normalize weights to sum to 100% of the calculated score
    final_score = min(total_score, 100)
    if final_score > 0:
        for factor in risk_factors:
            factor["weight"] = round((factor["weight"] / total_score) * 100)
    
    # Generate Summary and Action
    explanation_text = f"The risk score of {final_score} is primarily driven by "
    if sla_breached_flag:
        explanation_text += "a significant SLA breach and lack of recent engagement."
    elif age_score > 20:
        explanation_text += "its age and slow progress in the pipeline."
    else:
        explanation_text += "a combination of its source and low follow-up activity."

    recommended_action = "Initiate a follow-up call or personalized email today to re-engage and qualify this lead."
    if sla_breached_flag:
        recommended_action = "This lead has breached SLA. Prioritize immediate contact to mitigate risk and show commitment."

    # Add a disclaimer for small data samples
    disclaimer = None
    if lead.id < 50: # Assuming IDs are sequential and a proxy for data volume
        disclaimer = "Note: Risk assessment is based on a limited dataset and should be used as a directional signal."

    return {
        "lead_id": lead.id,
        "risk_score": final_score,
        "risk_factors": risk_factors,
        "explanation_text": explanation_text,
        "recommended_action": recommended_action,
        "disclaimer": disclaimer
    }
