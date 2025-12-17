from typing import List, Dict, Any
from .base import BaseIngestion
from app.schemas.lead import LeadCreate

class FBAdsIngestion(BaseIngestion):
    """Ingestion adapter for leads from Facebook Ads lead forms."""

    @property
    def source_name(self) -> str:
        return "fb_ads"

    @property
    def trust_score(self) -> float:
        return 0.6  # Lower initial trust

    def fetch(self) -> List[Dict[str, Any]]:
        """Mocks fetching data from the Facebook Graph API."""
        return [
            {
                "form_id": "123",
                "created_time": "2023-10-27T10:00:00+0000",
                "field_data": [
                    {"name": "full_name", "values": ["Andi Wijaya"]},
                    {"name": "email", "values": ["andi.w@example.com"]},
                    {"name": "phone_number", "values": ["+6281234567890"]},
                    {"name": "budget_range", "values": ["1-2 Bio"]}
                ]
            },
            {
                "form_id": "124",
                "created_time": "2023-10-27T11:00:00+0000",
                "field_data": [
                    {"name": "full_name", "values": ["Siti Aminah"]},
                    {"name": "email", "values": ["siti.a@example.com"]},
                    {"name": "phone_number", "values": ["+628111222333"]},
                    {"name": "budget_range", "values": ["> 2 Bio"]}
                ]
            }
        ]

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[LeadCreate]:
        """Normalizes FB Ads data into the canonical Lead schema."""
        normalized_leads = []
        for item in raw_data:
            field_map = {field["name"]: field["values"][0] for field in item["field_data"]}
            
            # Simple budget parsing logic
            budget_str = field_map.get("budget_range", "0").lower()
            budget = 0.0
            if "1-2 bio" in budget_str:
                budget = 1500000000
            elif "> 2 bio" in budget_str:
                budget = 2500000000

            normalized_leads.append(
                LeadCreate(
                    name=field_map.get("full_name", "Unknown"),
                    phone=field_map.get("phone_number", "N/A"),
                    email=field_map.get("email"),
                    source=self.source_name,
                    budget=budget,
                    notes=f"Lead from FB Ads form_id: {item['form_id']}",
                    status="new"
                )
            )
        return normalized_leads
