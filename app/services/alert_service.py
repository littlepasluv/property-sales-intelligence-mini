from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

# 1. Centralized Alert Rule Configuration
ALERT_RULES = {
    "ingestion_failure": {
        "threshold": 0, # Any failure triggers this
        "severity": "high",
        "message": "Ingestion failed for source: {source_name}",
        "check": lambda state: any(s.get("status") == "failure" for s in state.get("ingestion_status", {}).get("sources", {}).values())
    },
    "low_data_completeness": {
        "threshold": 70.0, # Percent
        "severity": "medium",
        "message": "Average data completeness is {actual:.1f}%, below the {threshold:.0f}% target.",
        "check": lambda state: state.get("data_quality", {}).get("avg_completeness", 100) < ALERT_RULES["low_data_completeness"]["threshold"]
    },
    "stale_data": {
        "threshold_minutes": 120,
        "severity": "medium",
        "message": "Data is stale. Last ingestion was {actual:.0f} minutes ago (threshold: {threshold} min).",
        "check": lambda state: state.get("data_freshness", {}).get("last_updated_at") and (datetime.now(timezone.utc) - datetime.fromisoformat(state["data_freshness"]["last_updated_at"])).total_seconds() / 60 > ALERT_RULES["stale_data"]["threshold_minutes"]
    },
    "low_insight_confidence": {
        "threshold": 50, # Score
        "severity": "low",
        "message": "Insight confidence score is {actual}, below the recommended level of {threshold}.",
        "check": lambda state: state.get("insight_quality", {}).get("score", 100) < ALERT_RULES["low_insight_confidence"]["threshold"]
    }
}

# 2. Backend Alert Evaluation Engine
def evaluate_alerts(
    ingestion_status: Dict, 
    data_quality: Dict, 
    data_freshness: Dict, 
    insight_quality: Dict
) -> List[Dict[str, Any]]:
    """
    Evaluates all defined alert rules against the current system state.
    """
    active_alerts = []
    
    system_state = {
        "ingestion_status": ingestion_status,
        "data_quality": data_quality,
        "data_freshness": data_freshness,
        "insight_quality": insight_quality
    }

    # Ingestion Failure Check
    if ALERT_RULES["ingestion_failure"]["check"](system_state):
        for source, results in ingestion_status.get("sources", {}).items():
            if results.get("status") == "failure":
                active_alerts.append({
                    "type": "ingestion_failure",
                    "severity": ALERT_RULES["ingestion_failure"]["severity"],
                    "message": ALERT_RULES["ingestion_failure"]["message"].format(source_name=source.upper()),
                    "detected_at": datetime.now(timezone.utc).isoformat()
                })

    # Data Completeness Check
    if ALERT_RULES["low_data_completeness"]["check"](system_state):
        actual = data_quality.get("avg_completeness", 0)
        active_alerts.append({
            "type": "low_data_completeness",
            "severity": ALERT_RULES["low_data_completeness"]["severity"],
            "message": ALERT_RULES["low_data_completeness"]["message"].format(actual=actual, threshold=ALERT_RULES["low_data_completeness"]["threshold"]),
            "detected_at": datetime.now(timezone.utc).isoformat()
        })

    # Stale Data Check
    if ALERT_RULES["stale_data"]["check"](system_state):
        last_updated_at = data_freshness.get("last_updated_at")
        if last_updated_at:
            actual = (datetime.now(timezone.utc) - datetime.fromisoformat(last_updated_at)).total_seconds() / 60
            active_alerts.append({
                "type": "stale_data",
                "severity": ALERT_RULES["stale_data"]["severity"],
                "message": ALERT_RULES["stale_data"]["message"].format(actual=actual, threshold=ALERT_RULES["stale_data"]["threshold_minutes"]),
                "detected_at": datetime.now(timezone.utc).isoformat()
            })
        
    # Low Insight Confidence Check
    if ALERT_RULES["low_insight_confidence"]["check"](system_state):
        actual = insight_quality.get("score", 0)
        active_alerts.append({
            "type": "low_insight_confidence",
            "severity": ALERT_RULES["low_insight_confidence"]["severity"],
            "message": ALERT_RULES["low_insight_confidence"]["message"].format(actual=actual, threshold=ALERT_RULES["low_insight_confidence"]["threshold"]),
            "detected_at": datetime.now(timezone.utc).isoformat()
        })

    return active_alerts
