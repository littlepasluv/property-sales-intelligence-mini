from fastapi import APIRouter, status, HTTPException
from typing import List
from app.schemas.lead import Lead, LeadCreate
from app.services import lead_service

router = APIRouter()

@router.post(
    "/", 
    response_model=Lead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lead"
)
async def create_lead(lead: LeadCreate):
    """
    Create a new lead.
    
    - **name**: Client name
    - **phone**: Contact number
    - **source**: Lead source (whatsapp, instagram, etc.)
    """
    return lead_service.create_lead(lead)

@router.get(
    "/", 
    response_model=List[Lead],
    summary="Get all leads"
)
async def get_leads():
    """
    Retrieve all leads.
    """
    return lead_service.get_all_leads()
