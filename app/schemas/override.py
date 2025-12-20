from pydantic import BaseModel

class DecisionOverride(BaseModel):
    by: str
    role: str
    reason: str
