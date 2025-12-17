from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from .followup import Followup  # Import the Followup schema

class LeadBase(BaseModel):
    name: str = Field(..., description="Name of the potential client", json_schema_extra={"example": "Budi Santoso"})
    phone: str = Field(..., description="Primary contact number (WhatsApp)", json_schema_extra={"example": "+628123456789"})
    email: Optional[str] = Field(None, description="Email address (optional)", json_schema_extra={"example": "budi@example.com"})
    source: str = Field("manual", description="Where the lead came from", json_schema_extra={"example": "whatsapp"})
    budget: Optional[float] = Field(None, description="Estimated budget", json_schema_extra={"example": 1500000000})
    notes: Optional[str] = Field(None, description="Agent's notes", json_schema_extra={"example": "Looking for 3BR"})
    status: str = Field("new", description="Current status", json_schema_extra={"example": "new"})

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    followups: List[Followup] = []  # Include followups in the main lead schema
    model_config = ConfigDict(from_attributes=True)

class LeadAnalytics(BaseModel):
    """Schema for a lead with calculated analytics fields."""
    id: int
    name: str
    status: str
    source: str
    age_days: int
    sla_breached: bool
    risk_score: int
    risk_level: str
    followup_count: int
    
    # Explainability fields
    risk_factors: List[Dict[str, Any]] = Field([], description="List of factors contributing to the risk score")
    explanation_text: str = Field("No explanation available.", description="Summary explanation of the lead's risk")
    recommended_action: str = Field("No specific action recommended.", description="Suggested next step for the agent")
    disclaimer: Optional[str] = Field(None, description="Disclaimer about the risk assessment")
    
    # Trust & Confidence fields
    confidence_score: float = Field(0.0, description="Confidence score (0-1) in the data quality and risk assessment")
    confidence_level: str = Field("Low", description="Confidence level (Low, Medium, High)")
    explainability_coverage: float = Field(0.0, description="Coverage of identified risk factors against expected ones")

    model_config = ConfigDict(from_attributes=True)
