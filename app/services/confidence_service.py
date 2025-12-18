from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.schemas.confidence import ConfidenceInput, ConfidenceScore, ConfidenceSignal, DataSource
from app.services.lead_service import get_all_leads
from app.ingestion.registry import registry
from app.services.explainability import generate_explanation

# --- Configuration ---
WEIGHTS = {
    "freshness": 0.35,
    "completeness": 0.25,
    "ingestion": 0.15,
    "source": 0.15,
    "validity": 0.10
}
DECAY_RATE_PER_HOUR = 2.0
SOURCE_TRUST = {"crm": 100, "api": 90, "scraper": 60, "manual": 70}

def map_score_to_status(score: float) -> str:
    if score >= 85: return "HIGH"
    elif score >= 60: return "MEDIUM"
    else: return "LOW"

def _calculate_freshness(last_updated: datetime) -> Tuple[float, str]:
    if not last_updated:
        return 0.0, "Data timestamp is missing."
    hours_diff = (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600
    score = max(0.0, min(100.0, 100.0 - (hours_diff * DECAY_RATE_PER_HOUR)))
    if score >= 100: msg = "Data is up-to-date."
    elif score >= 50: msg = f"Data is {int(hours_diff)} hours old."
    else: msg = f"Data is stale ({int(hours_diff)} hours old)."
    return score, msg

def _calculate_completeness(total: int, failed: int) -> Tuple[float, str]:
    if total <= 0:
        return 0.0, "No records processed."
    score = max(0.0, min(100.0, ((total - failed) / total) * 100.0))
    if score >= 100: msg = "Records are complete."
    elif score >= 70: msg = f"{failed} missing/failed records."
    else: msg = "Critical information is missing from many leads."
    return score, msg

def _calculate_ingestion_health(completeness_score: float) -> Tuple[float, str]:
    score = completeness_score
    if score > 90: msg = "Pipeline is healthy."
    else: msg = "Pipeline encountered errors."
    return score, msg

def _calculate_source_reliability(source_type: str) -> Tuple[float, str]:
    score = float(SOURCE_TRUST.get(source_type, 50))
    status = map_score_to_status(score).lower()
    return score, f"Source '{source_type}' is {status}."

def _calculate_validity(ingestion_score: float) -> Tuple[float, str]:
    score = max(0.0, ingestion_score - 5.0)
    if score > 90: msg = "Data format is valid."
    else: msg = "Potential anomalies detected."
    return score, msg

def calculate_confidence(input_data: ConfidenceInput) -> ConfidenceScore:
    freshness_score, freshness_msg = _calculate_freshness(input_data.last_updated)
    completeness_score, completeness_msg = _calculate_completeness(input_data.total_records, input_data.failed_records)
    ingestion_score, ingestion_msg = _calculate_ingestion_health(completeness_score)
    source_score, source_msg = _calculate_source_reliability(input_data.source_type.value)
    validity_score, validity_msg = _calculate_validity(ingestion_score)

    final_score = (
        (freshness_score * WEIGHTS["freshness"]) +
        (completeness_score * WEIGHTS["completeness"]) +
        (ingestion_score * WEIGHTS["ingestion"]) +
        (source_score * WEIGHTS["source"]) +
        (validity_score * WEIGHTS["validity"])
    )
    
    signals = [
        ConfidenceSignal(component="Data Freshness", status=map_score_to_status(freshness_score), message=freshness_msg),
        ConfidenceSignal(component="Data Completeness", status=map_score_to_status(completeness_score), message=completeness_msg),
        ConfidenceSignal(component="Ingestion Health", status=map_score_to_status(ingestion_score), message=ingestion_msg),
        ConfidenceSignal(component="Source Reliability", status=map_score_to_status(source_score), message=source_msg),
        ConfidenceSignal(component="Data Validity", status=map_score_to_status(validity_score), message=validity_msg)
    ]

    final_level = map_score_to_status(final_score)
    explanation = generate_explanation(final_score, final_level, [s.model_dump() for s in signals])

    return ConfidenceScore(
        score=round(final_score, 1),
        level=final_level,
        signals=signals,
        metrics={
            "freshness_score": freshness_score,
            "completeness_score": completeness_score,
            "ingestion_score": ingestion_score,
            "source_score": source_score,
            "validity_score": validity_score
        },
        explanation_summary=explanation["summary"],
        explanation_details=explanation["details"],
        decision_guidance=explanation["decision_guidance"]
    )

def get_system_confidence(db: Session) -> ConfidenceScore:
    leads = get_all_leads(db)
    ingestion_summary = registry.last_summary or {}

    input_data = ConfidenceInput(
        last_updated=ingestion_summary.get("end_time", datetime.now(timezone.utc)),
        total_records=ingestion_summary.get("total_processed", len(leads) or 0),
        failed_records=ingestion_summary.get("total_failed", 0),
        source_type=ingestion_summary.get("sources", [{}])[0].get("name", "manual")
    )
    
    return calculate_confidence(input_data)
