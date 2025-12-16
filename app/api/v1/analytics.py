from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.lead import LeadAnalytics
from app.services.lead_service import get_leads_with_analytics

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/risk_profile", response_model=List[LeadAnalytics])
def get_lead_risk_profile(db: Session = Depends(get_db)):
    """
    Retrieves all leads with their calculated risk and SLA analytics.
    This data is computed on-the-fly and not stored in the database.
    """
    analytics_data = get_leads_with_analytics(db)
    return analytics_data
