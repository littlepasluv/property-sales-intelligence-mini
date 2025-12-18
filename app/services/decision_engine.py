from typing import List, Dict, Any
from app.schemas.decision import DecisionRecommendation, RecommendationPriority, SuggestedOwner
from app.core.security import UserRole

def calculate_risk_score(metrics: dict) -> int:
    """
    Output: 0–100 risk score
    """
    weights = {
        "lead_conversion_rate": 0.30,
        "whatsapp_response_rate": 0.25,
        "data_completeness": 0.20,
        "avg_response_time": 0.15,
        "duplicate_rate": 0.10
    }

    normalized = {
        "lead_conversion_rate": max(0, 100 - (metrics.get("lead_conversion_rate", 0) * 10)),
        "whatsapp_response_rate": max(0, 100 - metrics.get("whatsapp_response_rate", 0)),
        "data_completeness": max(0, 100 - metrics.get("data_completeness", 0)),
        "avg_response_time": min(100, metrics.get("avg_response_time", 0) / 2),
        "duplicate_rate": min(100, metrics.get("duplicate_rate", 0) * 10)
    }

    score = sum(normalized[k] * w for k, w in weights.items())
    return int(min(100, score))

def generate_recommendations(risk_score: int, confidence: float, completeness: float) -> List[DecisionRecommendation]:
    """
    Generates recommendations based on a calculated risk score and other system metrics.
    """
    recommendations = []
    governance_flags = []
    if confidence < 60:
        governance_flags.append("low_confidence")
    if completeness < 70:
        governance_flags.append("data_gap")

    if risk_score >= 75:
        recommendations.append(DecisionRecommendation(
            title="CRITICAL: Address Data Duplication",
            recommendation="High duplication rate detected. Run data cleaning scripts to merge duplicate leads and prevent skewed analytics.",
            priority=RecommendationPriority.CRITICAL,
            confidence=int(confidence),
            rationale=f"Risk score is {risk_score}. The highest contributing factor is a high data duplication rate, which severely impacts trust.",
            impacted_metrics=["Data Quality", "Lead Count"],
            governance_flags=governance_flags,
            suggested_owner=SuggestedOwner.OPS
        ))
    
    if risk_score >= 50:
        recommendations.append(DecisionRecommendation(
            title="HIGH: Improve Lead Response Time",
            recommendation="Average lead response time is too high. Assign more resources to new leads or implement automated first-touch messages.",
            priority=RecommendationPriority.HIGH,
            confidence=int(confidence),
            rationale=f"Risk score is {risk_score}. Slow response times are a major cause of lead churn and missed opportunities.",
            impacted_metrics=["Time-to-Contact", "Conversion Rate"],
            governance_flags=governance_flags,
            suggested_owner=SuggestedOwner.SALES
        ))

    if risk_score >= 30:
        recommendations.append(DecisionRecommendation(
            title="MEDIUM: Boost WhatsApp Engagement",
            recommendation="WhatsApp response rates are below benchmark. A/B test new opening messages to improve engagement.",
            priority=RecommendationPriority.MEDIUM,
            confidence=int(confidence),
            rationale=f"Risk score is {risk_score}. Low engagement on a key channel indicates a need for process optimization.",
            impacted_metrics=["Response Rate", "Channel Performance"],
            governance_flags=governance_flags,
            suggested_owner=SuggestedOwner.MARKETING
        ))

    return recommendations

def filter_recommendations_by_persona(
    recommendations: List[DecisionRecommendation], 
    persona: UserRole
) -> List[DecisionRecommendation]:
    """
    Filters a list of recommendations based on the user's persona.
    """
    if persona == UserRole.FOUNDER:
        return [rec for rec in recommendations if rec.priority in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH]]
    
    elif persona == UserRole.SALES_MANAGER:
        return [rec for rec in recommendations if rec.suggested_owner in [SuggestedOwner.SALES, SuggestedOwner.MARKETING]]
        
    elif persona == UserRole.OPS_CRM:
        return [rec for rec in recommendations if rec.suggested_owner == SuggestedOwner.OPS]
        
    return recommendations
