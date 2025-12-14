from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LeadBase(BaseModel):
    """
    Shared properties for Lead data.
    Used for both creation (input) and reading (output).
    """
    name: str = Field(..., description="Name of the potential client", example="Budi Santoso")
    phone: str = Field(..., description="Primary contact number (WhatsApp)", example="+628123456789")
    email: Optional[str] = Field(None, description="Email address (optional)", example="budi@example.com")
    
    # Intelligence fields
    source: str = Field("manual", description="Where the lead came from (whatsapp, instagram, referral)", example="whatsapp")
    budget: Optional[float] = Field(None, description="Estimated budget in local currency", example=1500000000)
    notes: Optional[str] = Field(None, description="Agent's notes or specific requirements", example="Looking for 3BR near train station")
    
    # Pipeline status
    status: str = Field("new", description="Current status in the sales funnel", example="new")

class LeadCreate(LeadBase):
    """
    Schema for creating a new lead.
    Inherits all fields from LeadBase.
    """
    pass

class Lead(LeadBase):
    """
    Schema for reading a lead (API response).
    Includes system-generated fields.
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
