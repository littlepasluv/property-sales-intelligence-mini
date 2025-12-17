from datetime import datetime, timezone
from typing import List, Dict, Any
import logging
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
    This function is designed to be resilient and never raise an exception.
    """
    # Defensive defaults
    default_explanation = {
        "lead_id": getattr(lead, 'id', None),
        "risk_score": -1,
        "risk_factors": [],
        "explanation_text": "Risk analysis could not be completed due to missing data.",
        "recommended_action": "Please review lead data for completeness.",
        "disclaimer": "Assessment based on incomplete information."
    }

    try:
        if not isinstance(lead, Lead):
            return default_explanation

        risk_factors = []
        total_score = 0
        
        lead_age = get_lead_age_days(lead)
        followup_count = len(followups) if followups else 0
        sla_breached_flag = is_sla_breached(lead_age, getattr(lead, 'status', ''))

        # 1. SLA Breach Factor
        if sla_breached_flag:
            weight = RISK_SCORE_WEIGHTS.get("sla_breach", 0)
            total_score += weight
            risk_factors.append({
                "type": "sla_breach",
                "weight": weight,
                "detail": f"Lead has been in the '{lead.status}' stage for {lead_age} days, exceeding the {SLA_THRESHOLDS.get(lead.status, 'N/A')}-day SLA."
            })

        # 2. Lead Age / Stagnation Factor
        age_multiplier = RISK_SCORE_WEIGHTS.get("age_multiplier", 0)
        age_max_score = RISK_SCORE_WEIGHTS.get("age_max_score", 0)
        age_score = min(lead_age * age_multiplier, age_max_score)
        if age_score > 0:
            total_score += age_score
            risk_factors.append({
                "type": "stage_stagnation",
                "weight": age_score,
                "detail": f"Lead is {lead_age} days old, indicating slow movement through the pipeline."
            })

        # 3. Low Engagement Factor
        if followup_count <= 1:
            weight = RISK_SCORE_WEIGHTS.get("low_followup_penalty", 0)
            total_score += weight
            risk_factors.append({
                "type": "low_engagement",
                "weight": weight,
                "detail": f"Only {followup_count} follow-up(s) have been logged, suggesting minimal engagement."
            })

        # 4. Source-based Risk Factor
        source_penalty_map = RISK_SCORE_WEIGHTS.get("source_penalty", {})
        source_penalty = source_penalty_map.get(getattr(lead, 'source', ''), 0)
        if source_penalty > 0:
            total_score += source_penalty
            risk_factors.append({
                "type": "source_risk",
                "weight": source_penalty,
                "detail": f"Leads from '{lead.source}' are considered higher risk based on historical performance."
            })

        # Normalize weights
        final_score = min(total_score, 100)
        if final_score > 0 and total_score > 0:
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

        disclaimer = "Note: Risk assessment is based on a limited dataset and should be used as a directional signal." if getattr(lead, 'id', 0) < 50 else None

        return {
            "lead_id": lead.id,
            "risk_score": final_score,
            "risk_factors": risk_factors,
            "explanation_text": explanation_text,
            "recommended_action": recommended_action,
            "disclaimer": disclaimer
        }
    except Exception as e:
        logging.error(f"Error in explain_lead_risk for lead ID {getattr(lead, 'id', 'N/A')}: {e}")
        return default_explanation
