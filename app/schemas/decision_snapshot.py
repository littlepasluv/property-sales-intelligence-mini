from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class DecisionSnapshotRead(BaseModel):
    decision_id: str
    user_id: Optional[str]
    persona: str
    inputs: Dict[str, Any]
    rules_fired: List[str]
    weights: Dict[str, float]
    confidence: float
    outcome: Dict[str, Any]
    explanation: Dict[str, Any]
    status: str
    model_version: str
    created_at: datetime

    class Config:
        from_attributes = True
