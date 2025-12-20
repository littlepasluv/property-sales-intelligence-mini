from typing import Dict, Any, List

def evaluate_alerts(
    ingestion_status: Dict[str, Any],
    data_quality: Dict[str, Any],
    data_freshness: Dict[str, Any],
    insight_quality: Dict[str, Any]
) -> List[Dict[str, Any]]:
    alerts = []

    # Ingestion alerts
    if ingestion_status.get("total_failed", 0) > 0:
        alerts.append({
            "id": "ingestion_failure",
            "title": "Ingestion Failures Detected",
            "severity": "high",
            "description": f"{ingestion_status['total_failed']} records failed to ingest.",
            "category": "Data Pipeline"
        })

    # Data quality alerts
    if data_quality.get("completeness_score", 100) < 80:
        alerts.append({
            "id": "low_completeness",
            "title": "Low Data Completeness",
            "severity": "medium",
            "description": f"Data completeness is at {data_quality['completeness_score']}%.",
            "category": "Data Quality"
        })

    # Data freshness alerts
    if data_freshness.get("hours_since_last_update", 0) > 24:
        alerts.append({
            "id": "stale_data",
            "title": "Stale Data",
            "severity": "high",
            "description": f"Data has not been updated in {data_freshness['hours_since_last_update']} hours.",
            "category": "Data Freshness"
        })

    # Insight quality alerts
    if insight_quality.get("confidence_score", 100) < 60:
        alerts.append({
            "id": "low_confidence",
            "title": "Low Insight Confidence",
            "severity": "medium",
            "description": f"System confidence is low at {insight_quality['confidence_score']}%.",
            "category": "Insight Quality"
        })

    return alerts
