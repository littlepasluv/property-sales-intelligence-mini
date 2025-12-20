from pydantic import BaseModel

class ListingBase(BaseModel):
    address: str
    price: float
    agent_id: int

class ListingCreate(ListingBase):
    pass

class Listing(ListingBase):
    id: int

    class Config:
        from_attributes = True
