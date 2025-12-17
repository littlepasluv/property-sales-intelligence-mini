from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.lead import LeadCreate

class BaseIngestion(ABC):
    """
    Abstract base class for all data ingestion sources.
    It defines a standard interface for fetching and normalizing data.
    """
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """The unique name of the data source (e.g., 'fb_ads')."""
        pass

    @property
    @abstractmethod
    def trust_score(self) -> float:
        """A score from 0.0 to 1.0 indicating the reliability of the source."""
        pass

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetches raw data from the source.
        In a real implementation, this would involve API calls.
        """
        pass

    @abstractmethod
    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[LeadCreate]:
        """
        Transforms the raw data from the source into a list of
        standardized LeadCreate Pydantic models.
        """
        pass

    def run(self) -> List[LeadCreate]:
        """
        Executes the full fetch and normalize pipeline for the source.
        """
        raw_data = self.fetch()
        return self.normalize(raw_data)
