import pytest
from datetime import datetime
from detection.risk.correlation import CorrelationEngine
from detection.risk.factors import RiskFactorBuilder
from detection.risk.scorer import RiskScorer
from detection.risk.severity import SeverityClassifier
from schemas.risk import NormalizedAnomaly, CorrelationFactor
from models.database import LoginEvent
from core.config import get_settings

settings = get_settings()

def test_correlation_engine_multi_signal():
    anomalies = [
        NormalizedAnomaly(anomaly_id="1", event_id=1, user_id="u1", anomaly_type="T", detector="T", signal="TEMPORAL", feature="hour", detected_at=datetime.utcnow()),
        NormalizedAnomaly(anomaly_id="2", event_id=1, user_id="u1", anomaly_type="D", detector="D", signal="DEVICE", feature="fp", detected_at=datetime.utcnow()),
    ]
    event = LoginEvent(id=1, user_id="u1", auth_status="SUCCESS")
    
    factors = CorrelationEngine.evaluate(anomalies, event, [])
    assert len(factors) == 2
    factor_ids = [f.factor_id for f in factors]
    assert "MULTI_SIGNAL_SAME_EVENT" in factor_ids
    assert "OFF_HOURS_MULTI_ANOMALY" in factor_ids

def test_correlation_engine_auth_burst():
    anomalies = [
        NormalizedAnomaly(anomaly_id="1", event_id=1, user_id="u1", anomaly_type="A", detector="A", signal="AUTHENTICATION", feature="burst", detected_at=datetime.utcnow()),
    ]
    event = LoginEvent(id=1, user_id="u1", auth_status="SUCCESS")
    # 3 recent failures
    recent = [
        LoginEvent(id=2, user_id="u1", auth_status="FAILURE"),
        LoginEvent(id=3, user_id="u1", auth_status="FAILURE"),
        LoginEvent(id=4, user_id="u1", auth_status="FAILURE"),
    ]
    
    factors = CorrelationEngine.evaluate(anomalies, event, recent)
    assert len(factors) == 1
    assert factors[0].factor_id == "AUTH_FAILURE_BURST_THEN_SUCCESS"

def test_risk_scorer():
    anomalies = [
        NormalizedAnomaly(anomaly_id="1", event_id=1, user_id="u1", anomaly_type="T", detector="T", signal="TEMPORAL", feature="hour", detected_at=datetime.utcnow()),
    ]
    factors = RiskFactorBuilder.build_factors(anomalies, [])
    assert len(factors) == 1
    score = RiskScorer.calculate_score(factors)
    assert score == settings.WEIGHT_TEMPORAL
    
    severity = SeverityClassifier.classify(score)
    assert severity == "LOW"

def test_risk_scorer_clamp():
    from schemas.risk import RiskFactor
    factors = [RiskFactor(factor_id="1", name="1", description="", contribution=150.0, supporting_anomalies=[])]
    score = RiskScorer.calculate_score(factors)
    assert score == 100.0
