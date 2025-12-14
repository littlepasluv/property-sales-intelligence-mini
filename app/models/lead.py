from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Lead(Base):
    """
    SQLAlchemy model for lead records.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String, nullable=True, index=True)
    source = Column(String, index=True)
    budget = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    status = Column(String, default="new", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to Followup
    followups = relationship(
        "Followup", 
        back_populates="lead", 
        cascade="all, delete-orphan"
    )
