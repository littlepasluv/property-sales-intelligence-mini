from sqlalchemy import Column, String, Float, JSON, DateTime, Text, Enum as SAEnum
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DecisionOutcome(str, enum.Enum):
    SUCCESS = "success"
    NEUTRAL = "neutral"
    FAILURE = "failure"
    UNKNOWN = "unknown"

class DecisionMemory(Base):
    __tablename__ = "decision_memories"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    persona = Column(String, index=True, nullable=False)
    recommendation = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=False)
    rules_fired = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    approved_by = Column(String, nullable=True)
    approval_status = Column(String, default=ApprovalStatus.PENDING.value) # Stored as string for SQLite compat
    outcome = Column(String, default=DecisionOutcome.UNKNOWN.value) # Stored as string for SQLite compat
    feedback = Column(Text, nullable=True)
    learning_signal = Column(JSON, nullable=True)

    # Governance: No delete or update of core fields allowed by service layer
