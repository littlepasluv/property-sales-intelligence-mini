import time
import hashlib
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.decision_snapshot import DecisionSnapshot
from app.schemas.decision import DecisionRecommendation
from app.core.auth.security import UserRole

def generate_dtid() -> str:
    """
    Generates a unique Decision Trace ID (DTID).
    Format: dsc_<unix_timestamp>_<short_hash>
    """
    timestamp = int(time.time())
    # Use a random component or unique input to ensure uniqueness
    # Here using timestamp + simple hash for demonstration
    raw_str = f"{timestamp}-{time.process_time()}"
    short_hash = hashlib.sha256(raw_str.encode()).hexdigest()[:8]
    return f"dsc_{timestamp}_{short_hash}"

def determine_governance_status(confidence: float) -> str:
    """
    Determines the governance status based on confidence threshold.
    """
    if confidence < 65: # Using 65 as per requirement (0.65 or 65 depending on scale, assuming 0-100 scale based on existing code)
        return "REQUIRES_REVIEW"
    return "APPROVED"

def capture_decision_snapshot(
    db: Session,
    decision: DecisionRecommendation,
    user_id: str,
    persona: UserRole,
    inputs: Dict[str, Any],
    rules_fired: List[str],
    weights: Dict[str, float],
    model_version: str = "v1.0"
) -> DecisionSnapshot:
    """
    Persists a decision snapshot to the database.
    """
    dtid = generate_dtid()
    
    # Ensure decision object has the DTID (if we were modifying the object in place, 
    # but here we return the snapshot which has the ID)
    
    # Construct explanation structure as per requirement
    # Existing explanation in decision might need adaptation or we use it as is if it fits
    explanation_data = decision.explanation if decision.explanation else {}
    
    # Ensure 'why' and 'why_not' keys exist if not present
    if "why" not in explanation_data:
        explanation_data["why"] = explanation_data.get("contributing_factors", [])
    if "why_not" not in explanation_data:
        explanation_data["why_not"] = [] # Placeholder as current engine doesn't explicitly return rejected alternatives in a separate list

    status = determine_governance_status(decision.confidence)

    snapshot = DecisionSnapshot(
        decision_id=dtid,
        user_id=user_id,
        persona=persona.value,
        inputs=inputs,
        rules_fired=rules_fired,
        weights=weights,
        confidence=float(decision.confidence),
        outcome=decision.model_dump(mode='json'), # Store full decision object as outcome
        explanation=explanation_data,
        status=status,
        model_version=model_version
    )
    
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    
    return snapshot

def get_decision_snapshot(db: Session, decision_id: str) -> DecisionSnapshot:
    return db.query(DecisionSnapshot).filter(DecisionSnapshot.decision_id == decision_id).first()
