from typing import List
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport
from schemas.anomalies import AnomalyFinding, AnomalyType
from models.database import LoginEvent
from detection.anomalies.base import BaseAnomalyDetector, settings

class NetworkAnomalyDetector(BaseAnomalyDetector):
    """Detects network and IP anomalies."""
    
    @property
    def detector_name(self) -> str:
        return "network_detector"
        
    @property
    def is_enabled(self) -> bool:
        return settings.ANOMALY_NETWORK_ENABLED

    def evaluate(self, 
                 event: LoginEvent, 
                 features: EventBehavioralFeatures, 
                 comparison: BaselineComparisonResult, 
                 evidence: DeviationEvidenceReport,
                 recent_events: List[LoginEvent] = None) -> List[AnomalyFinding]:
        
        findings = []
        
        if "NETWORK" not in comparison.deviations:
            return findings
            
        net_dev = comparison.deviations["NETWORK"]
        if not net_dev.is_deviant:
            return findings
            
        # Find the specific evidence item
        evidence_item = next((e for e in evidence.evidence_items if e.dimension == "NETWORK" and e.is_deviant), None)
        if not evidence_item:
            return findings
            
        if evidence_item.feature_name == "ip_address":
            finding = AnomalyFinding(
                anomaly_id="",
                event_id=event.id,
                user_id=event.user_id,
                anomaly_type=AnomalyType.NETWORK_ANOMALY,
                detector=self.detector_name,
                signal="NETWORK",
                feature="ip_address",
                observed_value=str(evidence_item.observed_value),
                expected_state=str(evidence_item.baseline_expected),
                evidence={"evidence_text": evidence_item.evidence_text},
                explanation=f"User logged in from an unseen IP address ({evidence_item.observed_value}).",
                baseline_version=comparison.baseline_version,
                rule_id="NETWORK_UNSEEN_IP"
            )
            findings.append(finding)
            
        elif evidence_item.feature_name == "subnet":
            finding = AnomalyFinding(
                anomaly_id="",
                event_id=event.id,
                user_id=event.user_id,
                anomaly_type=AnomalyType.NETWORK_ANOMALY,
                detector=self.detector_name,
                signal="NETWORK",
                feature="subnet",
                observed_value=str(evidence_item.observed_value),
                expected_state=str(evidence_item.baseline_expected),
                evidence={"evidence_text": evidence_item.evidence_text},
                explanation=f"User logged in from an unseen network subnet ({evidence_item.observed_value}).",
                baseline_version=comparison.baseline_version,
                rule_id="NETWORK_UNSEEN_SUBNET"
            )
            findings.append(finding)

        return findings
