from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import List, Optional

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
    # --- Existing Fields ---
    score: float = Field(..., ge=0, le=100)
    level: str
    signals: List[ConfidenceSignal]
    metrics: dict

    # --- New Explainability & Governance Fields ---
    explanation_summary: Optional[str] = None
    explanation_details: Optional[List[str]] = None
    decision_guidance: Optional[str] = None
