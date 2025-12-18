from pydantic import BaseModel, Field
from typing import List
from enum import Enum
import uuid


class RecommendationPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SuggestedOwner(str, Enum):
    EXECUTIVE = "Executive"
    SALES = "Sales"
    MARKETING = "Marketing"
    OPS = "Ops"


class DecisionRecommendation(BaseModel):
    """
    Represents a single, actionable recommendation derived from system analytics
    to guide user decisions.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="A short, actionable headline for the recommendation.")
    recommendation: str = Field(..., description="A clear, instructive sentence on what action to take.")
    priority: RecommendationPriority = Field(..., description="The urgency of the recommendation.")
    confidence: float = Field(..., ge=0, le=100, description="The system's confidence in this recommendation (0-100).")
    rationale: str = Field(..., description="A plain-language explanation of why this action is suggested.")
    impacted_metrics: List[str] = Field(..., description="A list of metrics this action is expected to influence.")
    governance_flags: List[str] = Field(default=[],
                                        description="Flags indicating data quality or governance issues related to this recommendation.")
    suggested_owner: SuggestedOwner = Field(..., description="The team or role best suited to execute this action.")

    class Config:
        from_attributes = True
