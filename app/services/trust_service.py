from typing import List, Dict, Any
from app.models.lead import Lead
from datetime import datetime, timezone

def calculate_data_freshness(leads: List[Lead]) -> Dict[str, Any]:
    if not leads:
        return {"hours_since_last_update": 999}

    latest_lead = max(leads, key=lambda lead: lead.created_at)
    hours_diff = (datetime.now(timezone.utc) - latest_lead.created_at).total_seconds() / 3600
    return {"hours_since_last_update": round(hours_diff, 2)}
