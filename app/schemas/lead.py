from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.followup import Followup

class LeadBase(BaseModel):
    name: str = Field(..., min_length=1, description="Full name of the lead")
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number")
    email: Optional[EmailStr] = None
    source: str = Field(..., description="Lead source (e.g., 'facebook', 'referral')")
    budget: Optional[float] = None
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    status: str
    created_at: datetime
    followups: List[Followup] = []

    class Config:
        from_attributes = True
