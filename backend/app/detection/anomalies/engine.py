import logging
from typing import List
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport, BaselineStatus
from schemas.anomalies import AnomalyFinding
from models.database import LoginEvent
from detection.anomalies.temporal import TemporalAnomalyDetector
from detection.anomalies.device import DeviceAnomalyDetector
from detection.anomalies.location import LocationAnomalyDetector
from detection.anomalies.network import NetworkAnomalyDetector
from detection.anomalies.authentication import AuthenticationAnomalyDetector
from detection.anomalies.access import AccessPatternAnomalyDetector

logger = logging.getLogger("alias.detection.anomalies.engine")

class AnomalyDetectionEngine:
    """Central engine that runs all anomaly detectors and aggregates findings."""
    
    def __init__(self):
        self.detectors = [
            TemporalAnomalyDetector(),
            DeviceAnomalyDetector(),
            LocationAnomalyDetector(),
            NetworkAnomalyDetector(),
            AuthenticationAnomalyDetector(),
            AccessPatternAnomalyDetector()
        ]
        
    def evaluate(self, 
                 event: LoginEvent, 
                 features: EventBehavioralFeatures, 
                 comparison: BaselineComparisonResult, 
                 evidence: DeviationEvidenceReport,
                 recent_events: List[LoginEvent] = None) -> List[AnomalyFinding]:
        """Evaluates all enabled anomaly detectors against the factual evidence."""
        
        all_findings: List[AnomalyFinding] = []
        
        # Cold start handling: If baseline is insufficient, we DO NOT trigger standard historical anomalies,
        # but we might still trigger rules that don't depend strictly on history (e.g. impossible travel).
        # For strict conservatism, we skip evaluation if not READY, except for explicit rules if needed.
        # But per requirements: "Do not classify cold-start as anomalous."
        if comparison.comparison_status != BaselineStatus.READY:
            logger.info(f"Skipping anomaly detection for event {event.id} - Baseline status: {comparison.comparison_status}")
            return all_findings
            
        recent_events = recent_events or []
            
        for detector in self.detectors:
            if not detector.is_enabled:
                continue
                
            try:
                findings = detector.evaluate(event, features, comparison, evidence, recent_events)
                for f in findings:
                    f.anomaly_id = f.generate_id()
                    all_findings.append(f)
            except Exception as e:
                logger.error(f"Detector {detector.detector_name} failed for event {event.id}: {e}", exc_info=True)
                # Isolate failure and continue
                continue
                
        # Deduplicate findings based on anomaly_id
        unique_findings = {f.anomaly_id: f for f in all_findings}
        
        return list(unique_findings.values())

# Global singleton
anomaly_engine = AnomalyDetectionEngine()
