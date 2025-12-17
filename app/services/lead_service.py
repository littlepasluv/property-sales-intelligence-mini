from sqlalchemy.orm import Session, joinedload
from typing import List, Tuple
from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.analytics_service import process_lead_analytics
from app.services.explainability_service import explain_lead_risk
from app.services.trust_service import calculate_confidence_score, calculate_explainability_coverage
from app.core.cache import simple_cache, clear_cache

def upsert_lead(db: Session, lead_in: LeadCreate) -> Tuple[Lead, str]:
    """
    Creates a new lead or updates an existing one based on the phone number.
    Returns the lead object and a status string: 'inserted' or 'updated'.
    """
    phone = lead_in.phone
    existing_lead = db.query(Lead).filter(Lead.phone == phone).first()
    
    if existing_lead:
        # --- UPDATE (Merge) Logic ---
        status = "updated"
        if lead_in.source not in existing_lead.source.split(','):
            existing_lead.source = f"{existing_lead.source},{lead_in.source}"
        
        if lead_in.name and not existing_lead.name: existing_lead.name = lead_in.name
        if lead_in.email and not existing_lead.email: existing_lead.email = lead_in.email
        if lead_in.budget and not existing_lead.budget: existing_lead.budget = lead_in.budget
        if lead_in.notes: existing_lead.notes = f"{existing_lead.notes}\n---\n{lead_in.notes}"
        
        db_lead = existing_lead
    else:
        # --- INSERT Logic ---
        status = "inserted"
        db_lead = Lead(**lead_in.model_dump())
        db.add(db_lead)

    # The commit is handled by the ingestion registry per-source
    db.flush()
    db.refresh(db_lead)
    clear_cache()
    return db_lead, status

def create_lead(db: Session, lead_in: LeadCreate) -> Lead:
    """Simple lead creation. Ingestion should use upsert_lead."""
    db_lead = Lead(**lead_in.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    clear_cache()
    return db_lead

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
            
            explanation = explain_lead_risk(lead, lead.followups)
            lead_analytics.update(explanation)

            confidence = calculate_confidence_score(lead, lead_analytics)
            coverage = calculate_explainability_coverage(lead_analytics.get("risk_factors", []))
            lead_analytics.update({
                "confidence_score": confidence["score"],
                "confidence_level": confidence["level"],
                "explainability_coverage": coverage
            })

    return list(analytics_map.values())
