from fastapi import APIRouter, HTTPException, status
from typing import Dict

from app.ingestion.registry import registry

router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"]
)

@router.post("/run", status_code=status.HTTP_200_OK)
def run_ingestion() -> Dict:
    """
    Triggers the data ingestion process for all enabled sources and
    returns a detailed summary report.
    """
    try:
        summary = registry.ingest_all()
        return {
            "status": "ingestion_completed",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A critical error occurred during the ingestion process: {e}"
        )

@router.get("/sources")
def get_sources() -> Dict:
    """Returns a list of available and enabled ingestion sources."""
    return {
        "available": registry.get_available_sources(),
        "enabled": list(registry.enabled_sources)
    }
