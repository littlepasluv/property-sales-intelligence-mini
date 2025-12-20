from fastapi import APIRouter, Depends
from app.schemas.listing import Listing
from app.services import listing_service
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/listings", response_model=List[Listing])
async def read_listings(db: Session = Depends(get_db)):
    """
    Retrieve all property listings.
    """
    return listing_service.get_all_listings(db)
