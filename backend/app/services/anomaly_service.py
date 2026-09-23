import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from models.database import AnomalyRecord, LoginEvent
from schemas.anomalies import AnomalyFinding, AnomalyDetectionResponse
from schemas.baseline import BaselineComparisonResult, EventBehavioralFeatures, DeviationEvidenceReport
from detection.anomalies.engine import anomaly_engine

logger = logging.getLogger("alias.services.anomaly_service")

class AnomalyService:
    
    @staticmethod
    def evaluate_and_persist(db: Session, 
                             event: LoginEvent, 
                             features: EventBehavioralFeatures, 
                             comparison: BaselineComparisonResult, 
                             evidence: DeviationEvidenceReport) -> AnomalyDetectionResponse:
        
        # Get recent events for rules like Auth Burst and Impossible Travel
        recent_events = db.query(LoginEvent).filter(
            LoginEvent.user_id == event.user_id,
            LoginEvent.id != event.id
        ).order_by(LoginEvent.timestamp.desc()).limit(10).all()
        
        # Run detection
        findings = anomaly_engine.evaluate(event, features, comparison, evidence, recent_events)
        
        # Persist findings idempotently
        for finding in findings:
            existing = db.query(AnomalyRecord).filter(AnomalyRecord.anomaly_id == finding.anomaly_id).first()
            if not existing:
                record = AnomalyRecord(
                    anomaly_id=finding.anomaly_id,
                    event_id=finding.event_id,
                    user_id=finding.user_id,
                    anomaly_type=finding.anomaly_type,
                    detector=finding.detector,
                    signal=finding.signal,
                    feature=finding.feature,
                    observed_value=finding.observed_value,
                    expected_state=finding.expected_state,
                    evidence=finding.evidence,
                    explanation=finding.explanation,
                    baseline_version=finding.baseline_version,
                    rule_id=finding.rule_id,
                    detected_at=finding.detected_at
                )
                db.add(record)
        
        try:
            db.commit()
        except Exception as e:
            logger.error(f"Failed to persist anomalies for event {event.id}: {e}")
            db.rollback()
            
        return AnomalyDetectionResponse(
            event_id=event.id,
            user_id=event.user_id,
            baseline_version=comparison.baseline_version,
            anomalies=findings,
            detected_at=findings[0].detected_at if findings else event.timestamp,
            has_anomalies=len(findings) > 0
        )
