from fastapi import APIRouter, Depends
from app.schemas.listing import Listing
from app.services import listing_service
from typing import List

router = APIRouter()

@router.get("/listings", response_model=List[Listing])
async def read_listings():
    """
    Retrieve all property listings.
    """
    return listing_service.get_all_listings()
