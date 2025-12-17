from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class AuditLogBase(BaseModel):
    event_type: str = Field(..., description="Type of event being logged (e.g., 'risk_calculation').")
    entity_type: Optional[str] = Field(None, description="Type of the entity involved (e.g., 'lead').")
    entity_id: Optional[int] = Field(None, description="ID of the entity involved.")
    actor: str = Field("system", description="Who performed the action (e.g., 'system', 'user_email').")
    persona: Optional[str] = Field(None, description="The persona context for the event (e.g., 'sales', 'founder').")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Key-value pairs of inputs to the decision.")
    decision: Dict[str, Any] = Field(..., description="The outcome or decision made.")
    confidence: Optional[float] = Field(None, description="The confidence score associated with the decision.")
    explainability_ref: Optional[str] = Field(None, description="A reference to where the explanation can be found.")

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: int
    event_id: uuid.UUID
    timestamp: datetime
    event_hash: Optional[str] = None

    class Config:
        from_attributes = True
