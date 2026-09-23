import pytest
from datetime import datetime, timedelta
from schemas.baseline import CanonicalBaseline, BaselineStatus, EventBehavioralFeatures
from detection.baseline.engine import BaselineProfileEngine
from detection.baseline.comparison_engine import BaselineComparisonEngine
from detection.baseline.deviation_evidence import DeviationEvidenceBuilder

class MockEvent:
    def __init__(self, **kwargs):
        self.timestamp = datetime.utcnow()
        self.auth_status = "SUCCESS"
        self.device_fingerprint = None
        self.ip_address = None
        self.location = None
        self.latitude = None
        self.longitude = None
        self.failed_attempts = 0
        self.access_pattern = None
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_baseline_versioning_determinism():
    """Test that CanonicalBaseline versioning is deterministic and ignores transient fields."""
    b1 = CanonicalBaseline(
        user_id="user1",
        total_logins=10,
        status=BaselineStatus.READY,
        updated_at=datetime.utcnow() - timedelta(days=1)
    )
    b1.generate_version()
    
    b2 = CanonicalBaseline(
        user_id="user1",
        total_logins=10,
        status=BaselineStatus.NO_BASELINE, # Different status shouldn't change version
        updated_at=datetime.utcnow() # Different timestamp shouldn't change version
    )
    b2.generate_version()
    
    assert b1.baseline_version == b2.baseline_version
    assert b1.baseline_version.startswith("bsl_")
    
    # Change actual data
    b3 = CanonicalBaseline(
        user_id="user1",
        total_logins=11,
        status=BaselineStatus.READY
    )
    b3.generate_version()
    assert b1.baseline_version != b3.baseline_version


def test_cold_start_handling():
    """Test NO_BASELINE and INSUFFICIENT_HISTORY logic in Profile Engine and Comparison Engine."""
    
    # 0 events -> NO_BASELINE
    b_none = BaselineProfileEngine.compile_baseline("user1", [])
    assert b_none.status == BaselineStatus.NO_BASELINE
    assert b_none.total_logins == 0
    
    # 3 events -> INSUFFICIENT_HISTORY (threshold is 5)
    events_few = [MockEvent(user_id="user1", auth_status="SUCCESS") for _ in range(3)]
    b_few = BaselineProfileEngine.compile_baseline("user1", events_few)
    assert b_few.status == BaselineStatus.INSUFFICIENT_HISTORY
    assert b_few.total_logins == 3
    
    # 5 events -> READY
    events_ready = [MockEvent(user_id="user1", auth_status="SUCCESS") for _ in range(5)]
    b_ready = BaselineProfileEngine.compile_baseline("user1", events_ready)
    assert b_ready.status == BaselineStatus.READY
    assert b_ready.total_logins == 5

    # Test Comparison Engine short-circuit
    features = EventBehavioralFeatures(
        user_id="user1",
        timestamp=datetime.utcnow(),
        hour_of_day=12,
        day_of_week=2,
        is_weekend=False,
        ip_address="10.0.0.1"
    )
    
    res_none = BaselineComparisonEngine.compare(features, b_none)
    assert res_none.comparison_status == BaselineStatus.NO_BASELINE
    assert res_none.has_deviations is False
    assert len(res_none.deviations) == 0
    
    ev_none = DeviationEvidenceBuilder.build_evidence(res_none)
    assert ev_none.comparison_status == BaselineStatus.NO_BASELINE
    assert ev_none.has_deviations is False
    assert "skipped" in ev_none.summary.lower()
    
    res_few = BaselineComparisonEngine.compare(features, b_few)
    assert res_few.comparison_status == BaselineStatus.INSUFFICIENT_HISTORY
    
    ev_few = DeviationEvidenceBuilder.build_evidence(res_few)
    assert ev_few.comparison_status == BaselineStatus.INSUFFICIENT_HISTORY
    assert "skipped" in ev_few.summary.lower()
