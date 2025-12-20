from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class DecisionProposal(Base):
    __tablename__ = "decision_proposals"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True) # e.g., "lead", "listing"
    entity_id = Column(Integer, index=True)
    
    risk_score = Column(Float)
    decision_level = Column(String) # "low", "medium", "high"
    
    original_recommendation = Column(String)
    final_decision = Column(String)
    rationale = Column(String)
    
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED, OVERRIDDEN, ESCALATED
    
    overridden = Column(Boolean, default=False)
    override_details = Column(JSON, nullable=True) # Stores reason, user_id, etc.
    
    reviewed_by = Column(String, nullable=True)
    review_note = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
    
    escalated = Column(Boolean, default=False)
