import pytest
from datetime import datetime
from detection.anomalies.temporal import TemporalAnomalyDetector
from detection.anomalies.device import DeviceAnomalyDetector
from detection.anomalies.location import LocationAnomalyDetector
from detection.anomalies.network import NetworkAnomalyDetector
from detection.anomalies.authentication import AuthenticationAnomalyDetector
from detection.anomalies.access import AccessPatternAnomalyDetector
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport, DeviationEvidence
from schemas.anomalies import AnomalyType
from models.database import LoginEvent

def test_temporal_detector():
    detector = TemporalAnomalyDetector()
    
    # Mock data
    event = LoginEvent(id=1, user_id="u1")
    features = EventBehavioralFeatures(user_id="u1", timestamp=datetime.utcnow(), hour_of_day=3, day_of_week=0, is_weekend=False, ip_address="1.1.1.1")
    
    comp = BaselineComparisonResult(user_id="u1", timestamp=features.timestamp)
    # add deviation
    from schemas.baseline import DimensionDeviation
    comp.deviations["TEMPORAL"] = DimensionDeviation(dimension="TEMPORAL", is_deviant=True)
    
    evidence = DeviationEvidenceReport(user_id="u1", timestamp=features.timestamp)
    evidence.evidence_items.append(DeviationEvidence(
        dimension="TEMPORAL", feature_name="hour_of_day", is_deviant=True, 
        observed_value=3, baseline_expected="[9,10,11]", evidence_text="test"
    ))
    
    findings = detector.evaluate(event, features, comp, evidence)
    assert len(findings) == 1
    assert findings[0].anomaly_type == AnomalyType.TEMPORAL_ANOMALY
    assert findings[0].feature == "hour_of_day"

def test_device_detector():
    detector = DeviceAnomalyDetector()
    event = LoginEvent(id=1, user_id="u1")
    features = EventBehavioralFeatures(user_id="u1", timestamp=datetime.utcnow(), hour_of_day=3, day_of_week=0, is_weekend=False, ip_address="1.1.1.1")
    
    comp = BaselineComparisonResult(user_id="u1", timestamp=features.timestamp)
    from schemas.baseline import DimensionDeviation
    comp.deviations["DEVICE"] = DimensionDeviation(dimension="DEVICE", is_deviant=True)
    
    evidence = DeviationEvidenceReport(user_id="u1", timestamp=features.timestamp)
    evidence.evidence_items.append(DeviationEvidence(
        dimension="DEVICE", feature_name="device_fingerprint", is_deviant=True, 
        observed_value="new_dev", baseline_expected="old_dev", evidence_text="test"
    ))
    
    findings = detector.evaluate(event, features, comp, evidence)
    assert len(findings) == 1
    assert findings[0].anomaly_type == AnomalyType.DEVICE_ANOMALY
    assert findings[0].feature == "device_fingerprint"

def test_location_detector_impossible_travel():
    detector = LocationAnomalyDetector()
    event = LoginEvent(id=2, user_id="u1", timestamp=datetime(2026,1,1,12,0,0))
    features = EventBehavioralFeatures(user_id="u1", timestamp=datetime(2026,1,1,12,0,0), hour_of_day=12, day_of_week=0, is_weekend=False, ip_address="1.1.1.1", latitude=40.7128, longitude=-74.0060) # NYC
    
    # 1 hour prior, was in London (Impossible travel!)
    prev_event = LoginEvent(id=1, user_id="u1", timestamp=datetime(2026,1,1,11,0,0), latitude=51.5074, longitude=-0.1278)
    
    comp = BaselineComparisonResult(user_id="u1", timestamp=features.timestamp)
    # no explicit deviation from phase 3 required for impossible travel in this logic
    
    evidence = DeviationEvidenceReport(user_id="u1", timestamp=features.timestamp)
    
    findings = detector.evaluate(event, features, comp, evidence, recent_events=[prev_event])
    assert len(findings) == 1
    assert findings[0].anomaly_type == AnomalyType.LOCATION_ANOMALY
    assert findings[0].feature == "geographic_velocity"
