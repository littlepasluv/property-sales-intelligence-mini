from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditLogCreate(BaseModel):
    event_type: str
    decision: Optional[str] = None
    details: Optional[str] = None
    persona: Optional[str] = None

class AuditLog(BaseModel):
    id: int
    event_id: str
    event_type: str
    decision: Optional[str]
    details: Optional[str]
    persona: Optional[str]
    created_at: datetime
    event_hash: Optional[str]

    class Config:
        from_attributes = True
