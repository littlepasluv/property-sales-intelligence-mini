from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException

from app.models.decision_proposal import DecisionProposal
from app.schemas.decision_review import DecisionReview

def review_decision(db: Session, proposal_id: int, payload: DecisionReview):
    proposal = db.query(DecisionProposal).filter(DecisionProposal.id == proposal_id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="Decision proposal not found")

    if proposal.status != "PENDING":
        raise HTTPException(status_code=400, detail="Decision already finalized")

    if payload.action not in ("APPROVE", "REJECT"):
        raise HTTPException(status_code=400, detail="Invalid action")

    proposal.status = payload.action
    proposal.reviewed_by = payload.reviewer
    proposal.review_note = payload.note
    proposal.decided_at = datetime.utcnow()

    db.commit()
    db.refresh(proposal)
    return proposal
