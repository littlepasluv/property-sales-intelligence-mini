from sqlalchemy.orm import Session, joinedload
from typing import List, Tuple
from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.analytics_service import process_lead_analytics
from app.services.explainability_service import generate_explanation
from app.services.trust_service import calculate_confidence_score, calculate_explainability_coverage
from app.core.cache import simple_cache, clear_cache

def upsert_lead(db: Session, lead_in: LeadCreate) -> Tuple[Lead, str]:
    # ... (existing code)
    pass

def create_lead(db: Session, lead_in: LeadCreate) -> Lead:
    # ... (existing code)
    pass

@simple_cache(ttl=120)
def get_all_leads(db: Session) -> List[Lead]:
    return db.query(Lead).options(joinedload(Lead.followups)).all()

@simple_cache(ttl=120)
def get_leads_with_analytics(db: Session) -> List[dict]:
    leads = get_all_leads(db)
    if not leads:
        return []
        
    analytics_data = process_lead_analytics(leads)
    analytics_map = {data['id']: data for data in analytics_data if 'id' in data}

    for lead in leads:
        if lead.id in analytics_map:
            lead_analytics = analytics_map[lead.id]
            
            # --- Generate Explanation ---
            risk_score = lead_analytics.get("risk_score", 0)
            risk_factors = lead_analytics.get("risk_factors", [])
            signals = [factor.get("description", "Unknown factor") for factor in risk_factors]
            
            explanation = generate_explanation(
                decision_type="risk_score",
                decision_value=str(risk_score),
                signals=signals
            )
            lead_analytics["explanation"] = explanation
            # --- End Explanation ---

            confidence = calculate_confidence_score(lead, lead_analytics)
            coverage = calculate_explainability_coverage(risk_factors)
            lead_analytics.update({
                "confidence_score": confidence["score"],
                "confidence_level": confidence["level"],
                "explainability_coverage": coverage
            })

    return list(analytics_map.values())
