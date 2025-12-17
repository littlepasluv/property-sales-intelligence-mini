from datetime import datetime, timezone
from typing import List, Dict, Any
import logging
from app.models.lead import Lead

# --- Constants ---
EXPECTED_RISK_FACTORS = ["sla_breach", "stage_stagnation", "low_engagement", "source_risk"]

# --- Confidence Score Calculation ---

def calculate_confidence_score(lead: Lead, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates a confidence score for a single lead.
    Designed to be resilient to missing data.
    """
    try:
        score = 1.0
        
        # 1. Data Completeness Penalty
        if not getattr(lead, 'email', None): score -= 0.1
        if not getattr(lead, 'budget', None): score -= 0.1
        if not getattr(lead, 'notes', None) or len(lead.notes) < 10: score -= 0.05

        # 2. Follow-up Count Bonus/Penalty
        followup_count = analytics_data.get("followup_count", 0)
        if followup_count > 2:
            score += 0.15
        elif followup_count == 0:
            score -= 0.2

        # 3. SLA Signal Consistency
        sla_breached = analytics_data.get("sla_breached", False)
        is_high_risk = analytics_data.get("risk_level") == "High"
        if sla_breached and not is_high_risk:
            score -= 0.1

        final_score = max(0, min(1, round(score, 2)))

        if final_score >= 0.8: level = "High"
        elif final_score >= 0.5: level = "Medium"
        else: level = "Low"
            
        return {"score": final_score, "level": level}
    except Exception as e:
        logging.error(f"Error in calculate_confidence_score for lead ID {getattr(lead, 'id', 'N/A')}: {e}")
        return {"score": 0.0, "level": "Error"}

# --- Explainability Coverage Calculation ---

def calculate_explainability_coverage(risk_factors: List[Dict[str, Any]]) -> float:
    """
    Calculates the percentage of expected risk factors that were identified.
    """
    try:
        if not risk_factors or not isinstance(risk_factors, list):
            return 0.0
        
        identified_factor_types = {factor['type'] for factor in risk_factors if 'type' in factor}
        coverage = len(identified_factor_types) / len(EXPECTED_RISK_FACTORS)
        
        return round(coverage, 2)
    except Exception as e:
        logging.error(f"Error in calculate_explainability_coverage: {e}")
        return 0.0

# --- Data Freshness Calculation ---

def calculate_data_freshness(leads: List[Lead]) -> Dict[str, Any]:
    """
    Calculates the data freshness score based on the most recent activity.
    """
    try:
        if not leads:
            return {"last_updated_at": None, "freshness_score": 0, "data_status": "empty"}

        # Gather all valid timestamps
        timestamps = [lead.created_at for lead in leads if lead and lead.created_at]
        for lead in leads:
            if lead and lead.followups:
                timestamps.extend([f.created_at for f in lead.followups if f and f.created_at])
        
        if not timestamps:
            return {"last_updated_at": None, "freshness_score": 0, "data_status": "no_timestamps"}

        latest_timestamp = max(timestamps)
        
        if latest_timestamp.tzinfo is None:
            latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)

        delta_days = (datetime.now(timezone.utc) - latest_timestamp).days

        if delta_days < 1: score = 100
        elif delta_days <= 3: score = 80
        elif delta_days <= 7: score = 60
        else: score = 40
            
        return {
            "last_updated_at": latest_timestamp.isoformat(),
            "freshness_score": score
        }
    except Exception as e:
        logging.error(f"Error in calculate_data_freshness: {e}")
        return {"last_updated_at": None, "freshness_score": 0, "data_status": "error"}
