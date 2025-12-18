from typing import Dict, Any
from app.services.decision_engine import calculate_risk_score
from app.schemas.simulation import ScenarioResult, ImpactResult, SimulationResponse

def _map_risk_to_decision(risk_score: int) -> Dict[str, str]:
    """Maps a risk score to a decision level and priority."""
    if risk_score >= 75:
        return {"decision": "CRITICAL", "priority": "P0"}
    if risk_score >= 50:
        return {"decision": "HIGH", "priority": "P1"}
    if risk_score >= 30:
        return {"decision": "MEDIUM", "priority": "P2"}
    return {"decision": "LOW", "priority": "P3"}

def simulate_scenario(
    base_metrics: Dict[str, Any],
    overrides: Dict[str, float]
) -> SimulationResponse:
    """
    Merges base metrics with simulation overrides, recalculates risk, and compares outcomes.
    """
    # 1. Calculate Baseline Score and Decision
    baseline_score = calculate_risk_score(base_metrics)
    baseline_decision = _map_risk_to_decision(baseline_score)
    baseline_result = ScenarioResult(risk_score=baseline_score, **baseline_decision)

    # 2. Apply Overrides to Create Simulated Metrics
    simulated_metrics = base_metrics.copy()
    for key, improvement in overrides.items():
        if key in simulated_metrics:
            # Apply relative improvement and clamp values
            original_value = simulated_metrics[key]
            new_value = original_value * (1 + improvement)
            # Clamp percentages between 0-100, other values can be clamped as needed
            if "rate" in key or "completeness" in key:
                simulated_metrics[key] = max(0, min(100, new_value))
            else:
                simulated_metrics[key] = max(0, new_value)

    # 3. Calculate Simulated Score and Decision
    simulated_score = calculate_risk_score(simulated_metrics)
    simulated_decision = _map_risk_to_decision(simulated_score)
    simulated_result = ScenarioResult(risk_score=simulated_score, **simulated_decision)

    # 4. Calculate Impact
    impact_result = ImpactResult(
        risk_delta=simulated_score - baseline_score,
        decision_changed=(baseline_result.decision != simulated_result.decision),
        priority_changed=(baseline_result.priority != simulated_result.priority)
    )

    return SimulationResponse(
        baseline=baseline_result,
        simulated=simulated_result,
        impact=impact_result
    )
