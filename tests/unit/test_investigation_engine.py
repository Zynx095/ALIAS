"""Unit tests for Phase 6 Investigation Engine."""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from models.database import LoginEvent, AnomalyRecord, RiskAssessment, InvestigationReport
from investigation.engine import InvestigationEngine

def test_evidence_collection_and_mock_llm(db_session: Session):
    # 1. Setup Data
    event = LoginEvent(
        user_id="test_ai_user",
        timestamp=datetime.utcnow(),
        ip_address="8.8.8.8",
        device_fingerprint="unknown-device",
        auth_status="SUCCESS"
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    import uuid
    anomaly = AnomalyRecord(
        anomaly_id=str(uuid.uuid4()),
        event_id=event.id,
        user_id=event.user_id,
        anomaly_type="GEO_VELOCITY",
        signal="LOCATION",
        detector="GeoVelocityDetector",
        feature="distance",
        observed_value=1500.0,
        expected_state="< 500",
        explanation="Impossible travel detected",
        rule_id="GEO_001"
    )
    db_session.add(anomaly)
    
    risk = RiskAssessment(
        risk_id=str(uuid.uuid4()),
        event_id=event.id,
        user_id=event.user_id,
        risk_score=75.0,
        severity="HIGH",
        scoring_version="test_v1",
        explanation="Multiple anomalies detected",
        risk_factors=[{"name": "Impossible Travel", "contribution": 50, "description": "Too fast"}]
    )
    db_session.add(risk)
    db_session.commit()
    
    # 2. Test Engine
    engine = InvestigationEngine(db_session)
    # Force Mock Provider
    from investigation.providers import MockLLMProvider
    engine.provider = MockLLMProvider()
    
    report = engine.evaluate_and_persist(event)
    
    assert report is not None
    assert report.event_id == event.id
    assert report.risk_score == 75.0
    assert report.severity == "HIGH"
    assert report.llm_provider == "mock-fallback"
    assert "Suspicious login activity" in report.summary
    assert "ip:8.8.8.8" in report.indicators
    assert "rule:GEO_001" in report.indicators
    assert len(report.recommendations) > 0
    assert report.observed_evidence["ip_address"] == "8.8.8.8"
    assert len(report.correlated_factors) == 1
    assert str(anomaly.id) in report.supporting_anomaly_ids

def test_investigation_idempotency(db_session: Session):
    event = LoginEvent(
        user_id="test_ai_user_2",
        timestamp=datetime.utcnow(),
        ip_address="8.8.8.8",
        auth_status="SUCCESS"
    )
    db_session.add(event)
    db_session.commit()
    
    engine = InvestigationEngine(db_session)
    report1 = engine.evaluate_and_persist(event)
    report2 = engine.evaluate_and_persist(event)
    
    assert report1.id == report2.id
    assert report1.investigation_id == report2.investigation_id
    
    # test force_reevaluate
    report3 = engine.evaluate_and_persist(event, force_reevaluate=True)
    assert report3.id == report1.id  # Same ID because it overwrites/updates the existing row
