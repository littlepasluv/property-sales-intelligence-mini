from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DecisionOutcome(str, Enum):
    SUCCESS = "success"
    NEUTRAL = "neutral"
    FAILURE = "failure"
    UNKNOWN = "unknown"

class DecisionMemoryCreate(BaseModel):
    persona: str
    recommendation: Dict[str, Any]
    confidence: float = Field(..., ge=0.0, le=1.0)
    rules_fired: List[str]

class DecisionFeedbackUpdate(BaseModel):
    approval_status: Optional[ApprovalStatus] = None
    outcome: Optional[DecisionOutcome] = None
    feedback: Optional[str] = None
    approved_by: Optional[str] = None

class DecisionMemoryRead(BaseModel):
    id: str
    persona: str
    recommendation: Dict[str, Any]
    confidence: float
    rules_fired: List[str]
    created_at: datetime
    approved_by: Optional[str]
    approval_status: str
    outcome: str
    feedback: Optional[str]
    learning_signal: Optional[Dict[str, float]]

    class Config:
        from_attributes = True

class LearningSignal(BaseModel):
    delta: float = Field(..., ge=-0.1, le=0.1)
    reason: str
