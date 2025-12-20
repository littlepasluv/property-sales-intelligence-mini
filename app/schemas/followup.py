from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class FollowupBase(BaseModel):
    lead_id: int
    note: str = Field(..., min_length=1, description="Details of the interaction")
    status: str = Field(default="pending", description="Outcome status (e.g., 'contacted')")
    next_contact_date: Optional[date] = None

class FollowupCreate(FollowupBase):
    pass

class Followup(FollowupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
