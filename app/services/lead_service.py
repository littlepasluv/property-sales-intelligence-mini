from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.analytics_service import process_lead_analytics
from app.services.explainability_service import explain_lead_risk
from app.services.trust_service import calculate_confidence_score, calculate_explainability_coverage
from app.services.audit_log_service import log_risk_calculation, log_sla_breach_detection
from app.core.cache import simple_cache, clear_cache

def create_lead(db: Session, lead_in: LeadCreate) -> Lead:
    """Create a new lead record and invalidate cache."""
    db_lead = Lead(**lead_in.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    clear_cache()  # Invalidate cache on new data
    return db_lead

@simple_cache(ttl=120)
def get_all_leads(db: Session) -> List[Lead]:
    """
    Get all lead records, eagerly loading their follow-ups.
    This function is cached.
    """
    return db.query(Lead).options(joinedload(Lead.followups)).all()

@simple_cache(ttl=120)
def get_leads_with_analytics(db: Session) -> List[dict]:
    """
    Retrieves all leads and enriches them with calculated analytics.
    This entire function is cached to prevent re-computation.
    """
    leads = get_all_leads(db)
    if not leads:
        return []
        
    analytics_data = process_lead_analytics(leads)
    analytics_map = {data['id']: data for data in analytics_data if 'id' in data}

    for lead in leads:
        if lead.id in analytics_map:
            lead_analytics = analytics_map[lead.id]
            
            # Integrate Explainability
            explanation = explain_lead_risk(lead, lead.followups)
            lead_analytics.update({
                "risk_factors": explanation.get("risk_factors", []),
                "explanation_text": explanation.get("explanation_text", "No explanation available."),
                "recommended_action": explanation.get("recommended_action", "No specific action recommended."),
                "disclaimer": explanation.get("disclaimer")
            })

            # Integrate Trust & Confidence
            confidence = calculate_confidence_score(lead, lead_analytics)
            coverage = calculate_explainability_coverage(lead_analytics["risk_factors"])
            lead_analytics.update({
                "confidence_score": confidence["score"],
                "confidence_level": confidence["level"],
                "explainability_coverage": coverage
            })

            # Audit Logging (runs even on cache hit if not separated, but acceptable for this scope)
            # For a more advanced setup, this would be decoupled.
            log_risk_calculation(
                db=db,
                lead_id=lead.id,
                inputs={"age": lead_analytics.get("age_days", 0), "status": lead.status, "source": lead.source},
                decision={"risk_score": lead_analytics.get("risk_score", 0), "risk_level": lead_analytics.get("risk_level", "N/A")},
                confidence=lead_analytics.get("confidence_score", 0),
                explanation=lead_analytics.get("explanation_text", "")
            )
            if lead_analytics.get("sla_breached"):
                log_sla_breach_detection(
                    db=db,
                    lead_id=lead.id,
                    inputs={"age": lead_analytics.get("age_days", 0), "status": lead.status},
                    decision={"sla_breached": True}
                )

    return list(analytics_map.values())
