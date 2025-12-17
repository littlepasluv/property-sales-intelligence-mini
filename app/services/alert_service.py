from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.audit_log_service import log_alert_creation
from app.core.cache import simple_cache

@simple_cache(ttl=300)
def generate_alerts(db: Session, analytics_data: List[Dict[str, Any]], persona: str) -> List[Dict[str, Any]]:
    """
    Generates a list of alerts based on analytics data and persona, and logs the events.
    This function is cached.
    """
    alerts = []
    
    if not analytics_data:
        return alerts

    sla_breached_leads = [d for d in analytics_data if d.get('sla_breached')]
    high_risk_leads = [d for d in analytics_data if d.get('risk_level') == 'High' and not d.get('sla_breached')]
    
    try:
        oldest_unattended = max(analytics_data, key=lambda x: x.get('age_days', 0))
    except (ValueError, TypeError):
        oldest_unattended = {"age_days": "N/A", "name": "N/A"}


    # Persona-Aware Messaging
    persona_map = {
        "founder": {
            "sla_title": "SLA Breaches Impacting Reputation",
            "sla_message": f"{len(sla_breached_leads)} leads have breached SLA, posing a risk to client trust.",
            "risk_title": "High-Risk Leads Signal Pipeline Weakness",
            "risk_message": f"{len(high_risk_leads)} leads are high-risk, indicating potential revenue loss.",
            "summary_title": "Daily Strategic Summary",
            "summary_message": f"Attention: {len(high_risk_leads)} high-risk leads and {len(sla_breached_leads)} SLA breaches require review. Oldest unattended lead is {oldest_unattended.get('age_days')} days old."
        },
        "sales": {
            "sla_title": "Urgent: Follow Up on Breached Leads",
            "sla_message": f"{len(sla_breached_leads)} leads need immediate follow-up. Start with: {', '.join([l.get('name', 'N/A') for l in sla_breached_leads[:2]])}.",
            "risk_title": "High-Risk Leads to Prioritize",
            "risk_message": f"Focus on these {len(high_risk_leads)} high-risk leads to keep the pipeline moving.",
            "summary_title": "Your Daily Action Summary",
            "summary_message": f"Today's focus: {len(high_risk_leads)} high-risk leads and {len(sla_breached_leads)} urgent SLA breaches. Oldest unattended lead: {oldest_unattended.get('name')} ({oldest_unattended.get('age_days')} days)."
        },
        "ops": {
            "sla_title": "Process Alert: SLA Compliance Failure",
            "sla_message": f"Process failure: {len(sla_breached_leads)} leads have breached SLA in stages: {', '.join(set([l.get('status', 'N/A') for l in sla_breached_leads]))}.",
            "risk_title": "High-Risk Leads Analysis",
            "risk_message": f"{len(high_risk_leads)} leads are high-risk. Investigate if this is due to process delays.",
            "summary_title": "Daily Operational Health Check",
            "summary_message": f"System status: {len(high_risk_leads)} high-risk leads, {len(sla_breached_leads)} SLA breaches. Oldest unattended lead is {oldest_unattended.get('age_days')} days old."
        }
    }

    messages = persona_map.get(persona, persona_map["sales"])

    # Alert Generation
    if sla_breached_leads:
        alerts.append({"type": "sla_breach", "severity": "high", "icon": "⏰", "title": messages["sla_title"], "message": messages["sla_message"]})
    if high_risk_leads:
        alerts.append({"type": "high_risk", "severity": "medium", "icon": "⚠️", "title": messages["risk_title"], "message": messages["risk_message"]})
    if analytics_data:
        alerts.append({"type": "summary", "severity": "low", "icon": "🔥", "title": messages["summary_title"], "message": messages["summary_message"]})

    # Audit logging
    log_alert_creation(db=db, persona=persona, inputs={"lead_count": len(analytics_data)}, alerts=alerts)

    return alerts
