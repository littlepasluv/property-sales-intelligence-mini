from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class AuditLogCreate(BaseModel):
    """
    Schema for creating a new audit log entry.
    """
    event_type: str
    decision: Optional[str] = None
    details: Optional[str] = None
    persona: Optional[str] = None

class AuditLog(AuditLogCreate):
    """
    Schema for reading an audit log entry from the database.
    """
    id: int
    event_id: uuid.UUID
    created_at: datetime # Changed from timestamp
    event_hash: Optional[str] = None

    class Config:
        from_attributes = True
