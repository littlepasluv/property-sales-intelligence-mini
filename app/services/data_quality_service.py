from typing import List, Dict, Any
from app.models.lead import Lead

# Define which fields are considered for completeness check
REQUIRED_FIELDS = ['name', 'phone', 'source', 'status']
OPTIONAL_FIELDS = ['email', 'budget', 'notes']
ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

def calculate_lead_completeness(lead: Lead) -> float:
    """Calculates the data completeness score for a single lead (0.0 to 1.0)."""
    if not isinstance(lead, Lead):
        return 0.0
    
    filled_fields = 0
    for field in ALL_FIELDS:
        value = getattr(lead, field, None)
        if value is not None and value != '':
            filled_fields += 1
            
    return filled_fields / len(ALL_FIELDS)

def analyze_data_quality(leads: List[Lead]) -> Dict[str, Any]:
    """
    Analyzes a list of leads to calculate overall data quality and confidence.
    """
    total_leads = len(leads)
    
    if total_leads == 0:
        return {
            "total_leads": 0,
            "avg_completeness": 0.0,
            "confidence_level": "Low",
            "warnings": ["No data available to analyze."]
        }

    # Calculate completeness and identify missing fields
    completeness_scores = []
    missing_field_counts = {field: 0 for field in REQUIRED_FIELDS}
    
    for lead in leads:
        completeness_scores.append(calculate_lead_completeness(lead))
        for field in REQUIRED_FIELDS:
            if not getattr(lead, field, None):
                missing_field_counts[field] += 1

    avg_completeness = (sum(completeness_scores) / total_leads) * 100

    # Determine confidence level
    if total_leads >= 30 and avg_completeness >= 80:
        confidence_level = "High"
    elif total_leads >= 10 or avg_completeness >= 50:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    # Generate warnings
    warnings = []
    if confidence_level == "Low":
        warnings.append("Confidence is Low due to a small dataset size and/or low data completeness.")
    elif confidence_level == "Medium":
        warnings.append("Confidence is Medium. Improve data entry to increase reliability.")
        
    for field, count in missing_field_counts.items():
        if count > 0:
            warnings.append(f"Critical field '{field}' is missing in {count} lead(s).")

    return {
        "total_leads": total_leads,
        "avg_completeness": round(avg_completeness, 2),
        "confidence_level": confidence_level,
        "warnings": warnings
    }
