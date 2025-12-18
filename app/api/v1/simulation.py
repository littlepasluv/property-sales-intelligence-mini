from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.services.analytics_service import get_key_metrics
from app.services.scenario_simulation_service import simulate_scenario

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.post("/simulate", response_model=SimulationResponse)
def run_what_if_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Runs a what-if scenario by applying relative improvements to live metrics
    and recalculating the resulting risk score and decision level.
    """
    try:
        # 1. Fetch live base metrics
        base_metrics = get_key_metrics(db)
        if not base_metrics:
            raise HTTPException(status_code=404, detail="Base analytics data is currently unavailable.")

        # 2. Run simulation
        simulation_result = simulate_scenario(
            base_metrics=base_metrics,
            overrides=request.overrides
        )
        
        return simulation_result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run simulation: {str(e)}"
        )
