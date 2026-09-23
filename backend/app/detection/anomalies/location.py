from typing import List
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport
from schemas.anomalies import AnomalyFinding, AnomalyType
from models.database import LoginEvent
from detection.anomalies.base import BaseAnomalyDetector, settings

class LocationAnomalyDetector(BaseAnomalyDetector):
    """Detects geographic anomalies."""
    
    @property
    def detector_name(self) -> str:
        return "location_detector"
        
    @property
    def is_enabled(self) -> bool:
        return settings.ANOMALY_LOCATION_ENABLED

    def evaluate(self, 
                 event: LoginEvent, 
                 features: EventBehavioralFeatures, 
                 comparison: BaselineComparisonResult, 
                 evidence: DeviationEvidenceReport,
                 recent_events: List[LoginEvent] = None) -> List[AnomalyFinding]:
        
        findings = []
        
        # Optional: Impossible Travel check
        if recent_events and len(recent_events) > 0 and features.latitude and features.longitude:
            last_event = recent_events[0] # assuming sorted descending? Wait, in anomaly_service, I sorted desc. So recent_events[0] is the most recent.
            if last_event.latitude and last_event.longitude and last_event.timestamp < features.timestamp:
                distance = self._haversine(features.latitude, features.longitude, last_event.latitude, last_event.longitude)
                time_diff_hours = (features.timestamp - last_event.timestamp).total_seconds() / 3600.0
                if time_diff_hours > 0:
                    speed = distance / time_diff_hours
                    if speed > settings.IMPOSSIBLE_TRAVEL_SPEED_KMH:
                        finding = AnomalyFinding(
                            anomaly_id="",
                            event_id=event.id,
                            user_id=event.user_id,
                            anomaly_type=AnomalyType.LOCATION_ANOMALY,
                            detector=self.detector_name,
                            signal="LOCATION",
                            feature="geographic_velocity",
                            observed_value=f"{speed:.2f} km/h",
                            expected_state=f"<= {settings.IMPOSSIBLE_TRAVEL_SPEED_KMH} km/h",
                            evidence={
                                "distance_km": distance,
                                "time_diff_hours": time_diff_hours,
                                "previous_location": f"{last_event.latitude}, {last_event.longitude}"
                            },
                            explanation=f"Impossible travel detected: {speed:.2f} km/h exceeds {settings.IMPOSSIBLE_TRAVEL_SPEED_KMH} km/h limit.",
                            baseline_version=comparison.baseline_version,
                            rule_id="LOCATION_IMPOSSIBLE_TRAVEL"
                        )
                        findings.append(finding)

        if "LOCATION" not in comparison.deviations:
            return findings
            
        loc_dev = comparison.deviations["LOCATION"]
        if not loc_dev.is_deviant:
            return findings
            
        evidence_item = next((e for e in evidence.evidence_items if e.dimension == "LOCATION" and e.is_deviant), None)
        if not evidence_item:
            return findings
            
        if evidence_item.feature_name == "location_name":
            finding = AnomalyFinding(
                anomaly_id="",
                event_id=event.id,
                user_id=event.user_id,
                anomaly_type=AnomalyType.LOCATION_ANOMALY,
                detector=self.detector_name,
                signal="LOCATION",
                feature="location_name",
                observed_value=str(evidence_item.observed_value),
                expected_state=str(evidence_item.baseline_expected),
                evidence={"evidence_text": evidence_item.evidence_text},
                explanation=f"User logged in from an unseen geographic location ({evidence_item.observed_value}).",
                baseline_version=comparison.baseline_version,
                rule_id="LOCATION_UNSEEN_REGION"
            )
        return findings

    def _haversine(self, lat1, lon1, lat2, lon2):
        """Calculate the great circle distance in kilometers between two points on the earth."""
        import math
        R = 6371.0 # Earth radius in kilometers
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
