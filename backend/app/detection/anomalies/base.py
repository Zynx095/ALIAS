from abc import ABC, abstractmethod
from typing import List
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport
from schemas.anomalies import AnomalyFinding
from core.config import get_settings
from models.database import LoginEvent

settings = get_settings()

class BaseAnomalyDetector(ABC):
    """Abstract base class for all anomaly detectors."""
    
    @property
    @abstractmethod
    def detector_name(self) -> str:
        """Name of the detector."""
        pass
        
    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Whether this detector is enabled via config."""
        pass

    @abstractmethod
    def evaluate(self, 
                 event: LoginEvent, 
                 features: EventBehavioralFeatures, 
                 comparison: BaselineComparisonResult, 
                 evidence: DeviationEvidenceReport,
                 recent_events: List[LoginEvent] = None) -> List[AnomalyFinding]:
        """Evaluates an event for anomalies.
        
        Args:
            event: The raw LoginEvent record from DB.
            features: The extracted behavioral features for this event.
            comparison: The multi-dimensional comparison result.
            evidence: The human-readable factual evidence report.
            recent_events: (Optional) List of recent events if the detector requires history (e.g. auth burst).
            
        Returns:
            List of AnomalyFinding. Returns empty list if no anomalies are found.
        """
        pass
