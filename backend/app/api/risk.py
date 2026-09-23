import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models.database import get_db, LoginEvent, AnomalyRecord, RiskAssessment
from schemas.risk import RiskAssessmentResponse, RiskFactor, CorrelationFactor, NormalizedAnomaly
from schemas.anomalies import AnomalyFinding
from core.config import get_settings
from detection.risk.engine import risk_engine

settings = get_settings()
logger = logging.getLogger("alias.api.risk")
router = APIRouter()

@router.get("/events/{event_id}/risk", response_model=RiskAssessmentResponse)
async def get_event_risk(event_id: int, db: Session = Depends(get_db)):
    """Retrieve the deterministic risk assessment for a specific event."""
    event = db.query(LoginEvent).filter(LoginEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="LoginEvent not found")
        
    record = db.query(RiskAssessment).filter(RiskAssessment.event_id == event_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="RiskAssessment not found for this event")
        
    return RiskAssessmentResponse(
        risk_id=record.risk_id,
        event_id=record.event_id,
        user_id=record.user_id,
        risk_score=record.risk_score,
        severity=record.severity,
        risk_factors=[RiskFactor(**f) for f in record.risk_factors] if record.risk_factors else [],
        correlation_factors=[CorrelationFactor(**c) for c in record.correlation_factors] if record.correlation_factors else [],
        correlated_anomalies=[NormalizedAnomaly(**a) for a in record.correlated_anomalies] if record.correlated_anomalies else [],
        explanation=record.explanation or "",
        scoring_version=record.scoring_version,
        created_at=record.created_at
    )

@router.post("/events/{event_id}/risk/evaluate", response_model=RiskAssessmentResponse)
async def evaluate_event_risk(event_id: int, db: Session = Depends(get_db)):
    """Manually evaluate risk for an event based on its anomalies."""
    event = db.query(LoginEvent).filter(LoginEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="LoginEvent not found")
        
    # Get recent events for correlation context
    window_start = event.timestamp - timedelta(minutes=settings.CORRELATION_WINDOW_MINUTES)
    recent_events = db.query(LoginEvent).filter(
        LoginEvent.user_id == event.user_id,
        LoginEvent.id != event.id,
        LoginEvent.timestamp >= window_start,
        LoginEvent.timestamp <= event.timestamp
    ).order_by(LoginEvent.timestamp.desc()).all()
    
    # Get persisted anomalies
    anomaly_records = db.query(AnomalyRecord).filter(AnomalyRecord.event_id == event.id).all()
    
    findings = []
    for r in anomaly_records:
        findings.append(AnomalyFinding(
            anomaly_id=r.anomaly_id,
            event_id=r.event_id,
            user_id=r.user_id,
            anomaly_type=r.anomaly_type,
            detector=r.detector,
            signal=r.signal,
            feature=r.feature,
            observed_value=r.observed_value,
            expected_state=r.expected_state,
            evidence=r.evidence or {},
            explanation=r.explanation,
            baseline_version=r.baseline_version,
            rule_id=r.rule_id,
            detected_at=r.detected_at
        ))
        
    response = risk_engine.evaluate_and_persist(db, event, findings, recent_events)
    return response
