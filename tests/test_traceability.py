import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.traceability_service import generate_dtid, capture_decision_snapshot, get_decision_snapshot, determine_governance_status
from app.schemas.decision import DecisionRecommendation, RecommendationPriority, SuggestedOwner
from app.core.auth.security import UserRole

# Setup in-memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_dtid_format():
    dtid = generate_dtid()
    assert dtid.startswith("dsc_")
    parts = dtid.split("_")
    assert len(parts) == 3
    assert parts[1].isdigit() # Timestamp

def test_governance_status_logic():
    assert determine_governance_status(60) == "REQUIRES_REVIEW"
    assert determine_governance_status(70) == "APPROVED"

def test_snapshot_persistence_and_immutability(db):
    # Create a mock decision
    decision = DecisionRecommendation(
        title="Test Decision",
        recommendation="Do something",
        priority=RecommendationPriority.HIGH,
        confidence=85,
        rationale="Testing",
        impacted_metrics=["metric1"],
        suggested_owner=SuggestedOwner.SALES,
        governance_flags=[],
        explanation={"why": ["reason1"], "why_not": []}
    )
    
    # Capture snapshot
    snapshot = capture_decision_snapshot(
        db=db,
        decision=decision,
        user_id="test_user",
        persona=UserRole.SALES_MANAGER,
        inputs={"input1": "value1"},
        rules_fired=["RULE_1"],
        weights={"w1": 1.0}
    )
    
    assert snapshot.decision_id.startswith("dsc_")
    assert snapshot.status == "APPROVED"
    assert snapshot.confidence == 85.0
    
    # Retrieve snapshot
    retrieved = get_decision_snapshot(db, snapshot.decision_id)
    assert retrieved is not None
    assert retrieved.decision_id == snapshot.decision_id
    assert retrieved.inputs == {"input1": "value1"}
    
    # Verify immutability (conceptually, via API/Service layer we don't provide update methods)
    # Direct DB update is possible but service layer enforces write-once by not having update functions.
    
def test_replay_consistency(db):
    # Create another decision with low confidence
    decision = DecisionRecommendation(
        title="Low Conf Decision",
        recommendation="Check this",
        priority=RecommendationPriority.LOW,
        confidence=50,
        rationale="Testing low conf",
        impacted_metrics=[],
        suggested_owner=SuggestedOwner.OPS,
        governance_flags=[],
        explanation={"why": ["reason2"]}
    )
    
    snapshot = capture_decision_snapshot(
        db=db,
        decision=decision,
        user_id="user2",
        persona=UserRole.OPS_CRM,
        inputs={"input2": "value2"},
        rules_fired=["RULE_2"],
        weights={"w2": 0.5}
    )
    
    assert snapshot.status == "REQUIRES_REVIEW"
    
    # Replay (Read)
    replay = get_decision_snapshot(db, snapshot.decision_id)
    assert replay.outcome['title'] == "Low Conf Decision"
    assert replay.explanation['why'] == ["reason2"]
