from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class DecisionFeedbackType(str, enum.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"

class DecisionFeedback(Base):
    __tablename__ = "decision_feedback"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(String, index=True, nullable=False)
    recommendation_title = Column(String, index=True, nullable=True) # Added for rule-based aggregation
    persona = Column(String, nullable=False)
    decision = Column(String, nullable=False) # Storing enum as string for SQLite compatibility ease
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
