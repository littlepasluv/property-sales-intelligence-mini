from typing import List, Dict, Any, Tuple

def _get_status_priority(status: str) -> int:
    """Helper to sort signals by severity."""
    if status == "CRITICAL":
        return 0
    if status == "WARNING":
        return 1
    return 2  # GOOD

def generate_explanation(
    confidence_score: float,
    confidence_level: str,
    driver_signals: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates a human-readable summary, details, and guidance for a confidence score.
    """
    # 1. Generate the high-level summary
    if confidence_level == "HIGH":
        summary = "Confidence is High. The system's data is fresh, complete, and reliable, supporting strategic decisions."
    elif confidence_level == "MEDIUM":
        summary = "Confidence is Medium. Core operations are safe, but strategic decisions require manual verification due to minor data quality issues."
    else:  # LOW
        summary = "Confidence is Low. It is recommended to pause high-stakes decisions until data health is restored."

    # 2. Triage signals to find the most important issues for details
    details = []
    sorted_signals = sorted(driver_signals, key=lambda s: _get_status_priority(s.get('status', 'GOOD')))
    
    for signal in sorted_signals[:3]:
        status = signal.get('status')
        component = signal.get('component')
        message = signal.get('message')

        if status == "CRITICAL":
            details.append(f"**{component} is CRITICAL:** {message} This significantly impacts data reliability.")
        elif status == "WARNING":
            details.append(f"**{component} is a WARNING:** {message} This may affect the accuracy of some metrics.")

    if not details and sorted_signals:
        details.append("✅ **All drivers are GOOD:** Data is fresh, complete, and sourced from reliable channels.")
        
    # 3. Generate decision guidance
    if confidence_level == "HIGH":
        guidance = "Proceed as planned. System is operating at full reliability."
    elif confidence_level == "MEDIUM":
        guidance = "Review recommended. Manual verification advised for high-stakes decisions."
    else:  # LOW
        guidance = "Action blocked until resolved. Data is not reliable for decision-making."

    return {
        "summary": summary,
        "details": details,
        "decision_guidance": guidance
    }
