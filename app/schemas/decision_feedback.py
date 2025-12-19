from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class DecisionFeedbackType(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"

class DecisionFeedbackCreate(BaseModel):
    recommendation_id: str
    recommendation_title: Optional[str] = None
    decision: DecisionFeedbackType
    reason: Optional[str] = None

class DecisionFeedbackRead(BaseModel):
    id: int
    recommendation_id: str
    recommendation_title: Optional[str]
    persona: str
    decision: DecisionFeedbackType
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
