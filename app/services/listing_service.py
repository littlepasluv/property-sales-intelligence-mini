from sqlalchemy.orm import Session
from typing import List
from app.models.listing import Listing
from app.schemas.listing import ListingCreate

def create_listing(db: Session, listing_in: ListingCreate) -> Listing:
    db_listing = Listing(**listing_in.model_dump())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_all_listings(db: Session) -> List[Listing]:
    return db.query(Listing).all()
