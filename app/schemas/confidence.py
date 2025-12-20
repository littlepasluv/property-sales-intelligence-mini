from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class DataSource(str, Enum):
    CRM = "crm"
    API = "api"
    SCRAPER = "scraper"
    MANUAL = "manual"

class ConfidenceInput(BaseModel):
    last_updated: datetime
    total_records: int
    failed_records: int
    source_type: DataSource

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
