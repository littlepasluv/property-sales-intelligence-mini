from sqlalchemy.orm import Session, joinedload
from typing import List

from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services.analytics_service import process_lead_analytics

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
    Retrieves all leads and enriches them with calculated
    analytics fields like SLA status and risk score.
    """
    leads = get_all_leads(db)
    return process_lead_analytics(leads)
