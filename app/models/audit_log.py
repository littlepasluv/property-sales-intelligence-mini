from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

def default_uuid():
    return str(uuid.uuid4())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, default=default_uuid)
    event_type = Column(String, index=True, nullable=False)
    entity_type = Column(String, index=True)
    entity_id = Column(Integer, index=True)
    actor = Column(String, nullable=False, default="system")
    persona = Column(String, index=True, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    inputs = Column(JSON, nullable=True)
    decision = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=True)
    explainability_ref = Column(String, nullable=True)
    event_hash = Column(String, nullable=True) # For future Web3 anchoring
