from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.audit_log_service import log_persona_insight_generation
from app.core.cache import simple_cache

@simple_cache(ttl=300)
def generate_all_persona_insights(db: Session, analytics_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Generates a dictionary of formatted insight strings for all personas and logs the events.
    This function is cached.
    """
    if not analytics_data:
        return {
            "Founder": "No lead data available to generate insights.",
            "Sales Manager": "No lead data available to generate insights.",
            "Operations Manager": "No lead data available to generate insights."
        }

    insights = {
        "Founder": _generate_founder_insights(analytics_data),
        "Sales Manager": _generate_sales_manager_insights(analytics_data),
        "Operations Manager": _generate_operations_manager_insights(analytics_data),
    }

    # Audit logging
    for persona, insight_text in insights.items():
        log_persona_insight_generation(
            db=db,
            persona=persona,
            inputs={"lead_count": len(analytics_data)},
            decision={"insight": insight_text}
        )

    return insights

def _generate_founder_insights(data: List[Dict[str, Any]]) -> str:
    # ... (existing code, no changes needed)
    total_leads = len(data)
    high_risk_leads = sum(1 for d in data if d.get('risk_level') == 'High')
    sla_breaches = sum(1 for d in data if d.get('sla_breached'))
    
    breach_rate = (sla_breaches / total_leads * 100) if total_leads > 0 else 0
    high_risk_rate = (high_risk_leads / total_leads * 100) if total_leads > 0 else 0

    insight = f"We have {total_leads} active leads, but {high_risk_rate:.0f}% are high-risk."
    risk = f"High SLA breach rate ({breach_rate:.0f}%) suggests potential brand damage." if breach_rate > 20 else "Opportunity to double-down on high-performing channels."
    recommendation = "Review lead management strategy to address high-risk leads." if high_risk_rate > 30 else "Invest in analytics to scale what works."

    return f"Founder / Executive\n• Key Insight: {insight}\n• Risk / Opportunity: {risk}\n• Recommended Action: {recommendation}"

def _generate_sales_manager_insights(data: List[Dict[str, Any]]) -> str:
    # ... (existing code, no changes needed)
    high_risk_leads = sorted([d for d in data if d.get('risk_level') == 'High'], key=lambda x: x.get('risk_score', 0), reverse=True)
    stale_leads = sorted([d for d in data if d.get('age_days', 0) > 7 and d.get('followup_count', 0) <= 1], key=lambda x: x.get('age_days', 0), reverse=True)

    if high_risk_leads:
        insight = f"Focus on these {len(high_risk_leads)} high-risk leads: {', '.join([l.get('name', 'N/A') for l in high_risk_leads[:3]])}."
    elif stale_leads:
        insight = f"Re-engage {len(stale_leads)} stale leads like {stale_leads[0].get('name', 'N/A')}."
    else:
        insight = "Pipeline is healthy. Great work!"

    action = f"Initiate follow-up for {len(stale_leads)} aging leads." if stale_leads else "Ensure new inbound leads are distributed."
    recommendation = f"Conduct a pipeline review for all {len(high_risk_leads)} high-risk leads." if high_risk_leads else "Share top-performing tactics with the team."

    return f"Sales Manager\n• Key Insight: {insight}\n• What to do TODAY: {action}\n• This WEEK: {recommendation}"

def _generate_operations_manager_insights(data: List[Dict[str, Any]]) -> str:
    # ... (existing code, no changes needed)
    sla_breaches = [d for d in data if d.get('sla_breached')]
    total_leads = len(data)
    breach_rate = (len(sla_breaches) / total_leads * 100) if total_leads > 0 else 0

    if sla_breaches:
        breached_statuses = {d.get('status', 'N/A') for d in sla_breaches}
        insight = f"{len(sla_breaches)} leads ({breach_rate:.0f}%) have breached SLA, primarily in '{', '.join(breached_statuses)}' stage."
    else:
        insight = "Excellent SLA compliance across all stages."

    gap = "Significant delay in moving leads, indicating a bottleneck." if breach_rate > 15 else "No major process gaps detected."
    suggestion = "Investigate bottleneck in breached stages. Consider automating reminders." if breach_rate > 15 else "Document the current successful workflow."

    return f"Operations / CRM Manager\n• Key Insight: {insight}\n• Process Gap: {gap}\n• Improvement Suggestion: {suggestion}"
