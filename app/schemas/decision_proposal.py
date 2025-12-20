from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DecisionProposalCreate(BaseModel):
    entity_type: str
    entity_id: int
    risk_score: float
    decision_level: str
    recommendation: str
    rationale: str

class DecisionProposalOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    risk_score: float
    decision_level: str
    original_recommendation: str
    final_decision: str
    rationale: str
    status: str
    overridden: bool
    override_details: Optional[Dict[str, Any]]
    reviewed_by: Optional[str]
    review_note: Optional[str]
    created_at: datetime
    decided_at: Optional[datetime]
    escalated: bool

    class Config:
        from_attributes = True
