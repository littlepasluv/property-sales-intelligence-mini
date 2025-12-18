from pydantic import BaseModel, Field
from typing import Dict, List

class LeadAnalytics(BaseModel):
    # ... (existing code)
    pass

class FollowupAnalytics(BaseModel):
    # ... (existing code)
    pass

class DashboardAnalytics(BaseModel):
    # ... (existing code)
    pass

# --- Confidence Drivers Schemas ---

class ConfidenceDriver(BaseModel):
    """
    Represents a single factor contributing to the overall confidence score.
    """
    name: str
    status: str  # e.g., "CRITICAL", "WARNING", "GOOD"
    score: float
    message: str

class ConfidenceDriversResponse(BaseModel):
    """
    The response model for the confidence drivers endpoint.
    """
    overall_confidence: str
    drivers: List[ConfidenceDriver]
