import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models.database import get_db, AnomalyRecord, LoginEvent
from schemas.anomalies import AnomalyFinding, AnomalyDetectionResponse

logger = logging.getLogger("alias.api.anomalies")
router = APIRouter()

@router.get("/events/{event_id}/anomalies", response_model=AnomalyDetectionResponse)
async def get_event_anomalies(event_id: int, db: Session = Depends(get_db)):
    """Retrieve anomaly findings for a specific event."""
    event = db.query(LoginEvent).filter(LoginEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="LoginEvent not found")
        
    all_anom = db.query(AnomalyRecord).all()
    logger.info(f"DEBUG ANOMALIES: total in DB={len(all_anom)}, event_ids={[r.event_id for r in all_anom]}")
    
    records = db.query(AnomalyRecord).filter(AnomalyRecord.event_id == event_id).all()
    
    findings = []
    for r in records:
        finding = AnomalyFinding(
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
        )
        findings.append(finding)
        
    return AnomalyDetectionResponse(
        event_id=event.id,
        user_id=event.user_id,
        baseline_version=findings[0].baseline_version if findings else None,
        anomalies=findings,
        detected_at=findings[0].detected_at if findings else event.timestamp,
        has_anomalies=len(findings) > 0
    )

@router.post("/events/{event_id}/anomalies/evaluate", response_model=AnomalyDetectionResponse)
async def evaluate_event_anomalies(event_id: int, db: Session = Depends(get_db)):
    """Manually evaluate an existing event for anomalies."""
    from schemas.baseline import CanonicalBaseline, BaselineStatus
    from detection.baseline.feature_extractor import BehavioralFeatureExtractor
    from detection.baseline.comparison_engine import BaselineComparisonEngine
    from detection.baseline.deviation_evidence import DeviationEvidenceBuilder
    from services.anomaly_service import AnomalyService
    from models.database import UserBaseline
    
    event = db.query(LoginEvent).filter(LoginEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="LoginEvent not found")
        
    features = BehavioralFeatureExtractor.extract_features(event)
    db_baseline = db.query(UserBaseline).filter(UserBaseline.user_id == event.user_id).first()
    
    if not db_baseline or db_baseline.status == BaselineStatus.NO_BASELINE:
        baseline = CanonicalBaseline(
            user_id=event.user_id,
            total_logins=0,
            status=BaselineStatus.NO_BASELINE
        )
    else:
        baseline = CanonicalBaseline(
            user_id=event.user_id,
            total_logins=db_baseline.login_count,
            temporal=db_baseline.typical_hours or {},
            device=db_baseline.known_devices or {},
            location=db_baseline.known_locations or {},
            network=db_baseline.known_ips or {},
            authentication=db_baseline.auth_profile or {},
            access_pattern=db_baseline.access_patterns or {},
            status=db_baseline.status,
            baseline_version=db_baseline.version
        )
        
    features.baseline_version = baseline.baseline_version
    comparison_result = BaselineComparisonEngine.compare(features, baseline)
    evidence_report = DeviationEvidenceBuilder.build_evidence(comparison_result)
    
    # Run anomaly detection
    response = AnomalyService.evaluate_and_persist(db, event, features, comparison_result, evidence_report)
    
    return response
