from pydantic import BaseModel
from typing import Dict, Any

class SimulationRequest(BaseModel):
    overrides: Dict[str, float]

class SimulationResponse(BaseModel):
    baseline: Dict[str, Any]
    simulated: Dict[str, Any]
    impact: Dict[str, Any]
