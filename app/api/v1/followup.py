from fastapi import APIRouter
from app.schemas.followup import Followup
from app.services import followup_service
from typing import List

router = APIRouter()

@router.get("/followups", response_model=List[Followup])
async def read_followups():
    """
    Retrieve all followups.
    """
    return followup_service.get_all_followups()
