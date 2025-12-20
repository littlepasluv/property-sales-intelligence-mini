from pydantic import BaseModel
from typing import Optional

class DecisionReview(BaseModel):
    action: str
    reviewer: str
    note: Optional[str] = None
