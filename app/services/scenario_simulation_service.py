from typing import Dict, Any

def simulate_scenario(base_metrics: Dict[str, Any], overrides: Dict[str, float]) -> Dict[str, Any]:
    simulated_metrics = base_metrics.copy()
    for key, value in overrides.items():
        if key in simulated_metrics:
            simulated_metrics[key] *= (1 + value)

    # Dummy risk calculation
    baseline_risk = base_metrics.get("duplicate_rate", 0) * 10
    simulated_risk = simulated_metrics.get("duplicate_rate", 0) * 10

    return {
        "baseline": {"risk_score": baseline_risk, "decision": "low"},
        "simulated": {"risk_score": simulated_risk, "decision": "low"},
        "impact": {"risk_delta": simulated_risk - baseline_risk, "decision_changed": False}
    }
