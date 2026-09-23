"""Unit tests for Phase 3.5 - 3.10 Behavioral Baseline Expansion & Comparison."""
import pytest
from datetime import datetime, timezone

from models.database import LoginEvent
from detection.baseline.network_model import NetworkBehaviorModel
from detection.baseline.auth_model import AuthenticationBehaviorModel
from detection.baseline.access_model import AccessPatternModel
from detection.baseline.engine import BaselineProfileEngine
from detection.baseline.feature_extractor import BehavioralFeatureExtractor
from detection.baseline.comparison_engine import BaselineComparisonEngine
from detection.baseline.deviation_evidence import DeviationEvidenceBuilder


def make_mock_event(
    user_id="test.user@acme.corp",
    ip="192.168.1.50",
    device="device_hash_1",
    location="New York, USA",
    lat=40.7128,
    lon=-74.0060,
    timestamp=datetime(2026, 9, 21, 10, 0, 0),
    auth_status="SUCCESS",
    failed_attempts=0,
    access_pattern="DIRECT"
):
    return LoginEvent(
        user_id=user_id,
        ip_address=ip,
        device_fingerprint=device,
        location=location,
        latitude=lat,
        longitude=lon,
        timestamp=timestamp,
        auth_status=auth_status,
        failed_attempts=failed_attempts,
        access_pattern=access_pattern
    )


def test_network_behavior_model_subnets():
    """Verify NetworkBehaviorModel extracts subnets and IP versions."""
    events = [
        make_mock_event(ip="192.168.1.10"),
        make_mock_event(ip="192.168.1.20"),
        make_mock_event(ip="10.0.0.5"),
        make_mock_event(ip="2001:db8::1")
    ]
    profile = NetworkBehaviorModel.build_profile(events)

    assert "192.168.1.0/24" in profile.known_subnets
    assert "10.0.0.0/24" in profile.known_subnets
    assert "IPv4" in profile.ip_versions_seen
    assert "IPv6" in profile.ip_versions_seen
    assert profile.subnet_usage_counts["192.168.1.0/24"] == 2


def test_authentication_behavior_model():
    """Verify AuthenticationBehaviorModel accurately summarizes attempts and failure rates."""
    events = [
        make_mock_event(auth_status="SUCCESS", failed_attempts=0),
        make_mock_event(auth_status="SUCCESS", failed_attempts=1),
        make_mock_event(auth_status="FAILURE", failed_attempts=2),
        make_mock_event(auth_status="SUCCESS", failed_attempts=0)
    ]
    profile = AuthenticationBehaviorModel.build_profile(events)

    assert profile.total_attempts == 4
    assert profile.successful_logins == 3
    assert profile.failed_logins == 1
    assert profile.failure_rate == 0.25
    assert profile.typical_failed_attempts_max == 2
    assert profile.typical_failed_attempts_mean == 0.75
    assert profile.last_auth_status == "SUCCESS"


def test_access_pattern_model():
    """Verify AccessPatternModel profiles access modes."""
    events = [
        make_mock_event(access_pattern="DIRECT"),
        make_mock_event(access_pattern="DIRECT"),
        make_mock_event(access_pattern="VPN"),
        make_mock_event(access_pattern="DIRECT")
    ]
    profile = AccessPatternModel.build_profile(events)

    assert "DIRECT" in profile.known_access_patterns
    assert "VPN" in profile.known_access_patterns
    assert "DIRECT" in profile.primary_access_patterns
    assert profile.access_pattern_counts["DIRECT"] == 3
    assert profile.access_pattern_counts["VPN"] == 1
    assert profile.last_seen_access_pattern == "DIRECT"


def test_feature_extractor_from_dict():
    """Verify BehavioralFeatureExtractor works with dicts and extracts proper features."""
    raw_event = {
        "user_id": "sarah.connors@acme.corp",
        "timestamp": "2026-09-21T14:30:00Z",
        "ip_address": "150.101.100.100",
        "device_fingerprint": "dev_test_abc",
        "location": "San Francisco, USA",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "auth_status": "SUCCESS",
        "failed_attempts": 1,
        "access_pattern": "VPN"
    }
    features = BehavioralFeatureExtractor.extract_features(raw_event)

    assert features.user_id == "sarah.connors@acme.corp"
    assert features.hour_of_day == 14
    assert features.ip_address == "150.101.100.100"
    assert features.subnet == "150.101.100.0/24"
    assert features.ip_version == "IPv4"
    assert features.device_fingerprint == "dev_test_abc"
    assert features.auth_status == "SUCCESS"
    assert features.failed_attempts == 1
    assert features.access_pattern == "VPN"


def test_baseline_comparison_and_evidence():
    """Verify BaselineComparisonEngine and DeviationEvidenceBuilder end-to-end."""
    # 1. Build a history of 10 events for a user
    events = [
        make_mock_event(
            timestamp=datetime(2026, 9, 21, 10, 0, 0),
            ip="192.168.1.10",
            device="laptop_work",
            location="San Francisco, USA",
            lat=37.7749,
            lon=-122.4194,
            auth_status="SUCCESS",
            failed_attempts=0,
            access_pattern="DIRECT"
        )
        for _ in range(10)
    ]
    canonical_baseline = BaselineProfileEngine.compile_baseline("sarah.connors@acme.corp", events)

    # 2. Test a normal event (should have NO deviations)
    normal_event = make_mock_event(
        timestamp=datetime(2026, 9, 21, 10, 30, 0),
        ip="192.168.1.10",
        device="laptop_work",
        location="San Francisco, USA",
        lat=37.7749,
        lon=-122.4194,
        auth_status="SUCCESS",
        failed_attempts=0,
        access_pattern="DIRECT"
    )
    features_normal = BehavioralFeatureExtractor.extract_features(normal_event)
    comparison_normal = BaselineComparisonEngine.compare(features_normal, canonical_baseline)
    evidence_normal = DeviationEvidenceBuilder.build_evidence(comparison_normal)

    assert comparison_normal.has_deviations is False
    assert evidence_normal.has_deviations is False
    assert len(evidence_normal.evidence_items) == 0
    assert "No behavioral deviations" in evidence_normal.summary

    # 3. Test an event deviating across multiple dimensions:
    # - Off-hours (03:00)
    # - New device (unknown_phone)
    # - New location (London, UK) with huge distance
    # - New IP (80.10.20.30)
    # - Auth failure with 3 failed attempts
    # - New access pattern (TOR)
    deviant_event = make_mock_event(
        timestamp=datetime(2026, 9, 21, 3, 0, 0),
        ip="80.10.20.30",
        device="unknown_phone",
        location="London, UK",
        lat=51.5074,
        lon=-0.1278,
        auth_status="FAILURE",
        failed_attempts=3,
        access_pattern="TOR"
    )
    features_deviant = BehavioralFeatureExtractor.extract_features(deviant_event)
    comparison_deviant = BaselineComparisonEngine.compare(features_deviant, canonical_baseline)
    evidence_deviant = DeviationEvidenceBuilder.build_evidence(comparison_deviant)

    assert comparison_deviant.has_deviations is True
    assert evidence_deviant.has_deviations is True
    assert "TEMPORAL" in evidence_deviant.deviating_dimensions
    assert "DEVICE" in evidence_deviant.deviating_dimensions
    assert "LOCATION" in evidence_deviant.deviating_dimensions
    assert "NETWORK" in evidence_deviant.deviating_dimensions
    assert "AUTHENTICATION" in evidence_deviant.deviating_dimensions
    assert "ACCESS_PATTERN" in evidence_deviant.deviating_dimensions

    # Check that evidence items are descriptive, objective strings
    for item in evidence_deviant.evidence_items:
        assert isinstance(item.evidence_text, str)
        assert len(item.evidence_text) > 0
        # STRICT BOUNDARY: Verify no threat intelligence / verdicts exist
        assert "malicious" not in item.evidence_text.lower()
        assert "risk_score" not in item.evidence_text.lower()
        assert "severity" not in item.evidence_text.lower()


def test_haversine_distance_calculation():
    """Verify distance calculation between SF and NY is approximately 4128 km."""
    sf_lat, sf_lon = 37.7749, -122.4194
    ny_lat, ny_lon = 40.7128, -74.0060

    dist = BaselineComparisonEngine._haversine_distance_km(sf_lat, sf_lon, ny_lat, ny_lon)
    assert dist is not None
    assert 4100 <= dist <= 4200
