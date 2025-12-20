from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.decision_memory import DecisionMemoryCreate, DecisionFeedbackUpdate, DecisionMemoryRead
from app.services import decision_memory_service
from app.core.auth.security import UserRole, require_roles, get_current_user, UserContext

router = APIRouter(
    prefix="/decisions",
    tags=["Decision Memory"]
)

@router.post("/memory", response_model=DecisionMemoryRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles([UserRole.FOUNDER, UserRole.OPS_CRM]))])
def create_decision_memory(
    decision_data: DecisionMemoryCreate,
    db: Session = Depends(get_db)
):
    """
    Stores a new decision in the append-only memory.
    Requires Admin/Ops role.
    """
    return decision_memory_service.store_decision(db, decision_data)

@router.post("/feedback/{memory_id}", response_model=DecisionMemoryRead, dependencies=[Depends(require_roles([UserRole.FOUNDER, UserRole.SALES_MANAGER]))])
def provide_decision_feedback(
    memory_id: str,
    feedback_data: DecisionFeedbackUpdate,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    """
    Allows a reviewer to provide feedback on a decision, updating its status and outcome.
    """
    feedback_data.approved_by = user.user_id
    return decision_memory_service.record_feedback(db, memory_id, feedback_data)

@router.get("/history", response_model=List[DecisionMemoryRead], dependencies=[Depends(require_roles([UserRole.FOUNDER, UserRole.SALES_MANAGER, UserRole.OPS_CRM, UserRole.VIEWER]))])
def get_decision_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieves a paginated history of all decisions from memory.
    """
    return decision_memory_service.get_decision_history(db, skip, limit)

@router.get("/learning-signals", response_model=List[DecisionMemoryRead], dependencies=[Depends(require_roles([UserRole.FOUNDER, UserRole.OPS_CRM]))])
def get_all_learning_signals(
    db: Session = Depends(get_db)
):
    """
    Retrieves all decisions that have generated a learning signal for review.
    """
    return decision_memory_service.get_learning_signals(db)
