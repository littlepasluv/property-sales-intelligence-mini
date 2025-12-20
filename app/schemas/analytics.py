from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ConfidenceSignal(BaseModel):
    component: str
    status: str
    message: str

class ConfidenceScore(BaseModel):
    score: float
    level: str
    signals: List[ConfidenceSignal]
    metrics: Dict[str, Any]
    explanation_summary: str
    explanation_details: List[str]
    decision_guidance: str

class SimulationRequest(BaseModel):
    overrides: Dict[str, float]

class SimulationResponse(BaseModel):
    baseline: Dict[str, Any]
    simulated: Dict[str, Any]
    impact: Dict[str, Any]
