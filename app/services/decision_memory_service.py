from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from app.models.decision_memory import DecisionMemory, ApprovalStatus, DecisionOutcome
from app.schemas.decision_memory import DecisionMemoryCreate, DecisionFeedbackUpdate, LearningSignal

# Governance: This service enforces append-only and controlled updates.
# No functions for deleting or modifying core recommendation data are provided.

def store_decision(db: Session, decision_data: DecisionMemoryCreate) -> DecisionMemory:
    """
    Stores a new decision in the memory table. This is an append-only operation.
    """
    new_memory = DecisionMemory(
        persona=decision_data.persona,
        recommendation=decision_data.recommendation,
        confidence=decision_data.confidence,
        rules_fired=decision_data.rules_fired,
        approval_status=ApprovalStatus.PENDING.value,
        outcome=DecisionOutcome.UNKNOWN.value
    )
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    return new_memory

def record_feedback(db: Session, memory_id: str, feedback_data: DecisionFeedbackUpdate) -> DecisionMemory:
    """
    Updates a decision memory record with feedback and generates a learning signal.
    Only feedback-related fields can be updated.
    """
    memory = db.query(DecisionMemory).filter(DecisionMemory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision memory not found")

    # Governance: Only allow updating feedback fields
    if feedback_data.approval_status:
        memory.approval_status = feedback_data.approval_status.value
    if feedback_data.outcome:
        memory.outcome = feedback_data.outcome.value
    if feedback_data.feedback:
        memory.feedback = feedback_data.feedback
    if feedback_data.approved_by:
        memory.approved_by = feedback_data.approved_by

    # Generate and store learning signal based on the new feedback
    learning_signal = generate_learning_signal(memory)
    memory.learning_signal = learning_signal.model_dump()

    db.commit()
    db.refresh(memory)
    return memory

def generate_learning_signal(memory: DecisionMemory) -> LearningSignal:
    """
    Generates a rule-based learning signal based on the decision's outcome and approval.
    This is a deterministic process, not ML.
    """
    # Rejected decisions always generate a negative signal
    if memory.approval_status == ApprovalStatus.REJECTED.value:
        return LearningSignal(delta=-0.05, reason="Decision was rejected by a human reviewer.")

    # Approved decisions generate signals based on outcome
    if memory.approval_status == ApprovalStatus.APPROVED.value:
        if memory.outcome == DecisionOutcome.SUCCESS.value:
            return LearningSignal(delta=0.02, reason="Approved decision led to a successful outcome.")
        if memory.outcome == DecisionOutcome.FAILURE.value:
            # Confidence decay for repeated failures could be implemented here
            # For now, a simple negative delta
            return LearningSignal(delta=-0.08, reason="Approved decision led to a failed outcome.")
    
    # Default neutral signal
    return LearningSignal(delta=0.0, reason="Neutral outcome or pending review.")
    # TODO D6.2: Implement logic to apply these learning signals to rule weights/confidence models
    # after human governance approval.

def get_decision_history(db: Session, skip: int = 0, limit: int = 100) -> List[DecisionMemory]:
    return db.query(DecisionMemory).order_by(DecisionMemory.created_at.desc()).offset(skip).limit(limit).all()

def get_learning_signals(db: Session) -> List[Dict[str, Any]]:
    """
    Retrieves all decisions that have a non-neutral learning signal.
    """
    return db.query(DecisionMemory).filter(DecisionMemory.learning_signal != None).order_by(DecisionMemory.created_at.desc()).all()
