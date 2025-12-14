from pydantic import BaseModel
from datetime import datetime

class Followup(BaseModel):
    id: int
    lead_id: int
    notes: str
    timestamp: datetime
