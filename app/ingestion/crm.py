from typing import List, Dict, Any
from .base import BaseIngestion
from app.schemas.lead import LeadCreate

class CRMIngestion(BaseIngestion):
    """Ingestion adapter for leads manually entered into a CRM."""

    @property
    def source_name(self) -> str:
        return "crm"

    @property
    def trust_score(self) -> float:
        return 0.9  # High trust

    def fetch(self) -> List[Dict[str, Any]]:
        """Mocks fetching data from a CRM API or database."""
        return [
            {
                "lead_id": "CRM-001",
                "contact_name": "David Chen",
                "contact_phone": "+6281987654321",
                "contact_email": "david.chen@example.com",
                "estimated_budget": 2000000000,
                "lead_status": "new",
                "created_by": "Sales Agent A",
                "summary": "Referral from existing client. Looking for investment property."
            }
        ]

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[LeadCreate]:
        """Normalizes CRM data into the canonical Lead schema."""
        normalized_leads = []
        for item in raw_data:
            normalized_leads.append(
                LeadCreate(
                    name=item["contact_name"],
                    phone=item["contact_phone"],
                    email=item["contact_email"],
                    source=self.source_name,
                    budget=item["estimated_budget"],
                    notes=item["summary"],
                    status=item["lead_status"]
                )
            )
        return normalized_leads
