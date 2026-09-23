from typing import List
from datetime import timedelta
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport
from schemas.anomalies import AnomalyFinding, AnomalyType
from models.database import LoginEvent
from detection.anomalies.base import BaseAnomalyDetector, settings

class AuthenticationAnomalyDetector(BaseAnomalyDetector):
    """Detects unusual authentication patterns (e.g., failure bursts)."""
    
    @property
    def detector_name(self) -> str:
        return "authentication_detector"
        
    @property
    def is_enabled(self) -> bool:
        return settings.ANOMALY_AUTH_ENABLED

    def evaluate(self, 
                 event: LoginEvent, 
                 features: EventBehavioralFeatures, 
                 comparison: BaselineComparisonResult, 
                 evidence: DeviationEvidenceReport,
                 recent_events: List[LoginEvent] = None) -> List[AnomalyFinding]:
        
        findings = []
        
        # Check explicit deviation from baseline (Phase 3)
        if "AUTHENTICATION" in comparison.deviations and comparison.deviations["AUTHENTICATION"].is_deviant:
            evidence_item = next((e for e in evidence.evidence_items if e.dimension == "AUTHENTICATION" and e.is_deviant), None)
            if evidence_item:
                finding = AnomalyFinding(
                    anomaly_id="",
                    event_id=event.id,
                    user_id=event.user_id,
                    anomaly_type=AnomalyType.AUTHENTICATION_ANOMALY,
                    detector=self.detector_name,
                    signal="AUTHENTICATION",
                    feature=evidence_item.feature_name,
                    observed_value=str(evidence_item.observed_value),
                    expected_state=str(evidence_item.baseline_expected),
                    evidence={"evidence_text": evidence_item.evidence_text},
                    explanation=f"Authentication behavior deviation: {evidence_item.evidence_text}",
                    baseline_version=comparison.baseline_version,
                    rule_id="AUTH_BEHAVIOR_DEVIATION"
                )
                findings.append(finding)
        
        # Phase 4 custom logic: Failure burst detection
        # Calculate recent failure count within the window
        if recent_events:
            window_start = features.timestamp - timedelta(minutes=settings.AUTH_FAILURE_WINDOW_MINUTES)
            recent_failures = [e for e in recent_events 
                               if getattr(e, "auth_status", "SUCCESS").upper() == "FAILURE" 
                               and e.timestamp >= window_start
                               and e.id != event.id]
                               
            if getattr(event, "auth_status", "SUCCESS").upper() == "FAILURE":
                recent_failures.append(event)
                
            failure_count = len(recent_failures)
            
            # Compare to typical max
            typical_max = comparison.deviations.get("AUTHENTICATION", None)
            baseline_max = 3 # fallback
            # Extract from canonical baseline if available
            # Wait, comparison object doesn't hold the baseline, but we can use the expected_state if needed,
            # For simplicity, if failures > AUTH_FAILURE_MULTIPLIER * max(1, historical_mean), or just simple threshold
            if failure_count > settings.AUTH_FAILURE_MULTIPLIER * 2: # heuristic if baseline missing specific field in comparison
                # But to stick to rules, let's just trigger if > threshold
                finding = AnomalyFinding(
                    anomaly_id="",
                    event_id=event.id,
                    user_id=event.user_id,
                    anomaly_type=AnomalyType.AUTHENTICATION_ANOMALY,
                    detector=self.detector_name,
                    signal="AUTHENTICATION",
                    feature="failure_burst",
                    observed_value=str(failure_count),
                    expected_state=f"<= {int(settings.AUTH_FAILURE_MULTIPLIER * 2)}",
                    evidence={"time_window_minutes": settings.AUTH_FAILURE_WINDOW_MINUTES, "failure_count": failure_count},
                    explanation=f"Observed {failure_count} failures within {settings.AUTH_FAILURE_WINDOW_MINUTES} minutes.",
                    baseline_version=comparison.baseline_version,
                    rule_id="AUTH_FAILURE_BURST"
                )
                findings.append(finding)

        return findings
