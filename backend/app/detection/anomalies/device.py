from typing import List
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport
from schemas.anomalies import AnomalyFinding, AnomalyType
from models.database import LoginEvent
from detection.anomalies.base import BaseAnomalyDetector, settings

class DeviceAnomalyDetector(BaseAnomalyDetector):
    """Detects anomalies in device usage."""
    
    @property
    def detector_name(self) -> str:
        return "device_detector"
        
    @property
    def is_enabled(self) -> bool:
        return settings.ANOMALY_DEVICE_ENABLED

    def evaluate(self, 
                 event: LoginEvent, 
                 features: EventBehavioralFeatures, 
                 comparison: BaselineComparisonResult, 
                 evidence: DeviationEvidenceReport,
                 recent_events: List[LoginEvent] = None) -> List[AnomalyFinding]:
        
        findings = []
        
        if "DEVICE" not in comparison.deviations:
            return findings
            
        device_dev = comparison.deviations["DEVICE"]
        if not device_dev.is_deviant:
            return findings
            
        # Find the specific evidence item
        evidence_item = next((e for e in evidence.evidence_items if e.dimension == "DEVICE" and e.is_deviant), None)
        if not evidence_item:
            return findings
            
        if evidence_item.feature_name == "device_fingerprint":
            finding = AnomalyFinding(
                anomaly_id="",
                event_id=event.id,
                user_id=event.user_id,
                anomaly_type=AnomalyType.DEVICE_ANOMALY,
                detector=self.detector_name,
                signal="DEVICE",
                feature="device_fingerprint",
                observed_value=str(evidence_item.observed_value),
                expected_state=str(evidence_item.baseline_expected),
                evidence={"evidence_text": evidence_item.evidence_text},
                explanation=f"User logged in from a completely new device fingerprint ({evidence_item.observed_value}).",
                baseline_version=comparison.baseline_version,
                rule_id="DEVICE_UNSEEN_FINGERPRINT"
            )
            findings.append(finding)

        return findings
