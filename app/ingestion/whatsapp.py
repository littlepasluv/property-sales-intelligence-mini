from typing import List, Dict, Any
from .base import BaseIngestion
from app.schemas.lead import LeadCreate

class WhatsAppIngestion(BaseIngestion):
    """Ingestion adapter for leads from WhatsApp chats."""

    @property
    def source_name(self) -> str:
        return "whatsapp"

    @property
    def trust_score(self) -> float:
        return 0.75  # Medium trust

    def fetch(self) -> List[Dict[str, Any]]:
        """Mocks fetching data from a WhatsApp Business API webhook."""
        return [
            {
                "from": "+6285611112222",
                "profile": {"name": "Bapak Eko"},
                "timestamp": "1698382800", # Unix timestamp
                "text": {"body": "Halo, saya tertarik dengan properti di BSD, budget 1M."}
            },
            {
                "from": "+6287733334444",
                "profile": {"name": "Ibu Ratna"},
                "timestamp": "1698386400",
                "text": {"body": "Selamat pagi, info dong untuk rumah 3 kamar tidur."}
            }
        ]

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[LeadCreate]:
        """Normalizes WhatsApp data into the canonical Lead schema."""
        normalized_leads = []
        for item in raw_data:
            # Simple budget parsing from text
            budget = 1000000000 if "1m" in item["text"]["body"].lower() else None

            normalized_leads.append(
                LeadCreate(
                    name=item["profile"]["name"],
                    phone=item["from"],
                    email=None,  # WhatsApp doesn't provide email
                    source=self.source_name,
                    budget=budget,
                    notes=f"Initial query: {item['text']['body']}",
                    status="new"
                )
            )
        return normalized_leads
