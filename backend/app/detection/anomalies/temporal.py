from typing import List
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport
from schemas.anomalies import AnomalyFinding, AnomalyType
from models.database import LoginEvent
from detection.anomalies.base import BaseAnomalyDetector, settings

class TemporalAnomalyDetector(BaseAnomalyDetector):
    """Detects anomalies in temporal behavior (login hours, weekend bounds)."""
    
    @property
    def detector_name(self) -> str:
        return "temporal_detector"
        
    @property
    def is_enabled(self) -> bool:
        return settings.ANOMALY_TEMPORAL_ENABLED

    def evaluate(self, 
                 event: LoginEvent, 
                 features: EventBehavioralFeatures, 
                 comparison: BaselineComparisonResult, 
                 evidence: DeviationEvidenceReport,
                 recent_events: List[LoginEvent] = None) -> List[AnomalyFinding]:
        
        findings = []
        
        # Look for temporal deviation in the comparison
        if "TEMPORAL" not in comparison.deviations:
            return findings
            
        temporal_dev = comparison.deviations["TEMPORAL"]
        if not temporal_dev.is_deviant:
            return findings
            
        # Find the specific evidence item
        evidence_item = next((e for e in evidence.evidence_items if e.dimension == "TEMPORAL" and e.is_deviant), None)
        if not evidence_item:
            return findings
            
        # If the feature is 'hour_of_day', it means login occurred outside typical hours.
        if evidence_item.feature_name == "hour_of_day":
            finding = AnomalyFinding(
                anomaly_id="", # Assigned by engine
                event_id=event.id,
                user_id=event.user_id,
                anomaly_type=AnomalyType.TEMPORAL_ANOMALY,
                detector=self.detector_name,
                signal="TEMPORAL",
                feature="hour_of_day",
                observed_value=str(evidence_item.observed_value),
                expected_state=str(evidence_item.baseline_expected),
                evidence={"evidence_text": evidence_item.evidence_text},
                explanation=f"User logged in at hour {evidence_item.observed_value}, which is outside their typical historical hours {evidence_item.baseline_expected}.",
                baseline_version=comparison.baseline_version,
                rule_id="TEMP_OUTSIDE_TYPICAL_HOURS"
            )
            findings.append(finding)
            
        # Weekend anomaly
        elif evidence_item.feature_name == "is_weekend":
            finding = AnomalyFinding(
                anomaly_id="",
                event_id=event.id,
                user_id=event.user_id,
                anomaly_type=AnomalyType.TEMPORAL_ANOMALY,
                detector=self.detector_name,
                signal="TEMPORAL",
                feature="is_weekend",
                observed_value=str(evidence_item.observed_value),
                expected_state=str(evidence_item.baseline_expected),
                evidence={"evidence_text": evidence_item.evidence_text},
                explanation=f"User logged in on a weekend, but historically has 0 weekend logins.",
                baseline_version=comparison.baseline_version,
                rule_id="TEMP_WEEKEND_NO_HISTORY"
            )
            findings.append(finding)

        return findings
