from typing import List, Dict, Any
from datetime import datetime, timezone

class IngestionRegistry:
    enabled_sources: List[str] = ["manual", "api"]
    last_summary: Dict[str, Any] = None

    def ingest_all(self) -> Dict[str, Any]:
        # Dummy ingestion logic
        summary = {
            "start_time": datetime.now(timezone.utc),
            "end_time": datetime.now(timezone.utc),
            "total_processed": 10,
            "total_failed": 0,
            "sources": [{"name": "manual", "status": "success"}]
        }
        self.last_summary = summary
        return summary

    def get_available_sources(self) -> List[str]:
        return ["manual", "api", "csv"]

registry = IngestionRegistry()
