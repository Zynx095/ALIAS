from typing import List
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport
from schemas.anomalies import AnomalyFinding, AnomalyType
from models.database import LoginEvent
from detection.anomalies.base import BaseAnomalyDetector, settings

class AccessPatternAnomalyDetector(BaseAnomalyDetector):
    """Detects anomalies in access patterns (e.g. unexpected VPN/TOR usage)."""
    
    @property
    def detector_name(self) -> str:
        return "access_pattern_detector"
        
    @property
    def is_enabled(self) -> bool:
        return settings.ANOMALY_ACCESS_ENABLED

    def evaluate(self, 
                 event: LoginEvent, 
                 features: EventBehavioralFeatures, 
                 comparison: BaselineComparisonResult, 
                 evidence: DeviationEvidenceReport,
                 recent_events: List[LoginEvent] = None) -> List[AnomalyFinding]:
        
        findings = []
        
        if "ACCESS_PATTERN" not in comparison.deviations:
            return findings
            
        acc_dev = comparison.deviations["ACCESS_PATTERN"]
        if not acc_dev.is_deviant:
            return findings
            
        # Find the specific evidence item
        evidence_item = next((e for e in evidence.evidence_items if e.dimension == "ACCESS_PATTERN" and e.is_deviant), None)
        if not evidence_item:
            return findings
            
        if evidence_item.feature_name == "access_pattern":
            finding = AnomalyFinding(
                anomaly_id="",
                event_id=event.id,
                user_id=event.user_id,
                anomaly_type=AnomalyType.ACCESS_PATTERN_ANOMALY,
                detector=self.detector_name,
                signal="ACCESS_PATTERN",
                feature="access_pattern",
                observed_value=str(evidence_item.observed_value),
                expected_state=str(evidence_item.baseline_expected),
                evidence={"evidence_text": evidence_item.evidence_text},
                explanation=f"User logged in via a previously unseen routing mechanism ({evidence_item.observed_value}).",
                baseline_version=comparison.baseline_version,
                rule_id="ACCESS_UNSEEN_PATTERN"
            )
            findings.append(finding)

        return findings
