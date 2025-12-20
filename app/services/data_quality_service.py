from typing import List, Dict, Any
from app.models.lead import Lead

def analyze_data_quality(leads: List[Lead]) -> Dict[str, Any]:
    total_leads = len(leads)
    if total_leads == 0:
        return {"completeness_score": 0}

    complete_leads = 0
    for lead in leads:
        if lead.email and lead.phone and lead.name:
            complete_leads += 1

    completeness_score = (complete_leads / total_leads) * 100
    return {"completeness_score": round(completeness_score, 2)}
