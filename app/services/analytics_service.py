from sqlalchemy.orm import Session
from typing import Dict, Any

def get_key_metrics(db: Session) -> Dict[str, Any]:
    """
    Dummy function to provide analytics metrics for the decision engine.
    In a real system, this would query and calculate metrics from the database.
    """
    # These values can be changed to test different recommendation rules.
    return {
        "lead_conversion_rate": 4.5,      # low score = high risk
        "whatsapp_response_rate": 12,     # low score = high risk
        "data_completeness": 65,          # low score = high risk
        "avg_response_time": 48,          # high score = high risk
        "duplicate_rate": 3,              # high score = high risk
    }
