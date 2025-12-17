from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.analytics_service import process_lead_analytics
from app.services.explainability_service import explain_lead_risk

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
    including risk scores and their explanations.
    """
    leads = get_all_leads(db)
    analytics_data = process_lead_analytics(leads)

    # Create a map for quick lookup
    analytics_map = {data['id']: data for data in analytics_data}

    # Integrate explainability for each lead
    for lead in leads:
        if lead.id in analytics_map:
            explanation = explain_lead_risk(lead, lead.followups)
            
            # Flatten the explanation dictionary into the analytics data
            analytics_map[lead.id].update({
                "risk_factors": explanation.get("risk_factors", []),
                "explanation_text": explanation.get("explanation_text", "No explanation available."),
                "recommended_action": explanation.get("recommended_action", "No specific action recommended."),
                "disclaimer": explanation.get("disclaimer")
            })

    return list(analytics_map.values())
