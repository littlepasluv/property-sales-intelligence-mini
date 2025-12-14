from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.followup import Followup, FollowupCreate
from app.services import followup_service

# Define the router with a specific prefix and tag
# This keeps the routing logic self-contained
router = APIRouter(
    prefix="/followups",
    tags=["Follow-ups"]
)

@router.post(
    "/",
    response_model=Followup,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new follow-up"
)
def create_followup(
    followup_in: FollowupCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new follow-up record for a lead.
    
    - **lead_id**: The ID of the lead (must exist)
    - **note**: Details of the interaction
    - **status**: Current status (pending, contacted, closed)
    - **next_contact_date**: Optional date for the next follow-up
    """
    return followup_service.create_followup(db=db, followup_in=followup_in)


@router.get(
    "/lead/{lead_id}",
    response_model=List[Followup],
    summary="Get follow-ups by lead"
)
def get_followups_by_lead(
    lead_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve the history of follow-ups for a specific lead.
    Results are ordered by creation date (newest first).
    """
    return followup_service.get_followups_by_lead(db=db, lead_id=lead_id)
