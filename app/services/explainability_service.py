from typing import List, Optional

def generate_explanation(decision_type: str, decision_value: str, signals: Optional[List[str]] = None) -> str:
    """
    Generates a human-readable explanation for a system decision.
    Designed for non-technical users (executives, sales managers).
    """
    if not signals:
        signals = []

    # --- Confidence Level Explanations ---
    if decision_type == "confidence_level":
        if decision_value == "High":
            base = "We have high confidence in this data because it is complete and recently updated."
        elif decision_value == "Medium":
            base = "Confidence is medium. While core data is available, some optional fields are missing or slightly outdated."
        else: # Low
            base = "Confidence is low due to missing critical data or stale records. Please review data sources."
        
        if signals:
            # Append the first signal as a specific reason if available
            # We clean the signal string to make it flow better in a sentence
            reason = signals[0].replace("✅ ", "").replace("⚠️ ", "").replace("🔥 ", "")
            return f"{base} Specifically: {reason}"
        return base

    # --- Risk Score Explanations ---
    elif decision_type == "risk_score":
        try:
            score = float(decision_value)
        except ValueError:
            score = 0

        if score >= 80:
            base = "This lead is flagged as high risk."
        elif score >= 50:
            base = "This lead carries a moderate level of risk."
        else:
            base = "This lead appears to be low risk."

        if signals:
             reason = signals[0].replace("✅ ", "").replace("⚠️ ", "").replace("🔥 ", "")
             return f"{base} Key factor: {reason}"
        return base

    # --- Default Fallback ---
    return f"The system determined a value of '{decision_value}' based on current data analysis."
