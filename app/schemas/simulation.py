from pydantic import BaseModel, Field
from typing import Dict, Optional

class SimulationRequest(BaseModel):
    overrides: Dict[str, float] = Field(..., description="Relative improvements to apply, e.g., {'sla_breach_rate': -0.2}")

class ScenarioResult(BaseModel):
    risk_score: int
    decision: str
    priority: str

class ImpactResult(BaseModel):
    risk_delta: int
    decision_changed: bool
    priority_changed: bool

class SimulationResponse(BaseModel):
    baseline: ScenarioResult
    simulated: ScenarioResult
    impact: ImpactResult
