from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from enum import Enum

class FollowupStatus(str, Enum):
    pending = "pending"
    contacted = "contacted"
    closed = "closed"

class FollowupBase(BaseModel):
    """
    Shared properties for Followup data.
    """
    lead_id: int = Field(..., description="ID of the lead this follow-up belongs to")
    note: str = Field(..., description="Details of the interaction", example="Customer asked for floor plan")
    status: str = Field("pending", description="Status of this interaction (pending, contacted, closed)", example="contacted")
    next_contact_date: Optional[date] = Field(None, description="When to contact the lead next", example="2023-12-25")

class FollowupCreate(FollowupBase):
    """
    Schema for creating a new follow-up.
    """
    pass

class Followup(FollowupBase):
    """
    Schema for reading a follow-up (API response).
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
