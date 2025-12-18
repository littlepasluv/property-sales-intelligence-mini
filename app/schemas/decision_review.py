from pydantic import BaseModel
from typing import Optional

class DecisionReview(BaseModel):
    action: str  # APPROVE or REJECT
    reviewer: str
    note: Optional[str] = None
