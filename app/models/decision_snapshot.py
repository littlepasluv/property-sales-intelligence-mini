from sqlalchemy import Column, String, Float, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class DecisionSnapshot(Base):
    __tablename__ = "decision_snapshots"

    decision_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=True)
    persona = Column(String, nullable=False)
    inputs = Column(JSON, nullable=False)
    rules_fired = Column(JSON, nullable=False)
    weights = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=False)
    outcome = Column(JSON, nullable=False)
    explanation = Column(JSON, nullable=False)
    status = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
