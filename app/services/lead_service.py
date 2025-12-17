from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.analytics_service import process_lead_analytics
from app.services.explainability_service import explain_lead_risk
from app.services.trust_service import calculate_confidence_score, calculate_explainability_coverage

def create_lead(db: Session, lead_in: LeadCreate) -> Lead:
    """Create a new lead record."""
    db_lead = Lead(**lead_in.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def get_all_leads(db: Session) -> List[Lead]:
    """
    Get all lead records, eagerly loading their follow-ups
    to prevent the N+1 query problem.
    """
    return db.query(Lead).options(joinedload(Lead.followups)).all()

def get_leads_with_analytics(db: Session) -> List[dict]:
    """
    Retrieves all leads and enriches them with calculated analytics,
    including risk, explainability, and trust scores.
    """
    leads = get_all_leads(db)
    analytics_data = process_lead_analytics(leads)
    analytics_map = {data['id']: data for data in analytics_data}

    for lead in leads:
        if lead.id in analytics_map:
            # 1. Get base analytics
            lead_analytics = analytics_map[lead.id]

            # 2. Integrate Explainability
            explanation = explain_lead_risk(lead, lead.followups)
            lead_analytics.update({
                "risk_factors": explanation.get("risk_factors", []),
                "explanation_text": explanation.get("explanation_text", "No explanation available."),
                "recommended_action": explanation.get("recommended_action", "No specific action recommended."),
                "disclaimer": explanation.get("disclaimer")
            })

            # 3. Integrate Trust & Confidence
            confidence = calculate_confidence_score(lead, lead_analytics)
            coverage = calculate_explainability_coverage(lead_analytics["risk_factors"])
            
            lead_analytics.update({
                "confidence_score": confidence["score"],
                "confidence_level": confidence["level"],
                "explainability_coverage": coverage
            })

    return list(analytics_map.values())
