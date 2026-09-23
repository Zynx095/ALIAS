import hashlib
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.database import LoginEvent, RiskAssessment
from schemas.anomalies import AnomalyFinding
from schemas.risk import RiskAssessmentResponse
from core.config import get_settings

from detection.risk.normalizer import AnomalyNormalizer
from detection.risk.correlation import CorrelationEngine
from detection.risk.factors import RiskFactorBuilder
from detection.risk.scorer import RiskScorer
from detection.risk.severity import SeverityClassifier
from detection.risk.explainer import RiskExplainer

settings = get_settings()

class RiskEngine:
    """Central orchestration engine for Phase 5."""
    
    @staticmethod
    def evaluate_and_persist(db: Session, event: LoginEvent, anomalies: List[AnomalyFinding], recent_events: List[LoginEvent] = None) -> RiskAssessmentResponse:
        recent_events = recent_events or []
        
        # 1. Normalize
        normalized = AnomalyNormalizer.normalize(anomalies)
        
        # 2. Correlate
        correlation_factors = CorrelationEngine.evaluate(normalized, event, recent_events)
        
        # 3. Build Risk Factors
        risk_factors = RiskFactorBuilder.build_factors(normalized, correlation_factors)
        
        # 4. Score
        score = RiskScorer.calculate_score(risk_factors)
        
        # 5. Severity
        severity = SeverityClassifier.classify(score)
        
        # 6. Explain
        explanation = RiskExplainer.generate_explanation(score, severity, risk_factors)
        
        # Determine deterministic risk_id
        # Use event_id + engine version. Risk is 1:1 with event evaluation for a given engine version.
        risk_key = f"{event.id}_{settings.RISK_ENGINE_VERSION}"
        risk_id = hashlib.sha256(risk_key.encode()).hexdigest()[:16]
        
        # 7. Persist
        existing = db.query(RiskAssessment).filter(RiskAssessment.risk_id == risk_id).first()
        if not existing:
            record = RiskAssessment(
                risk_id=risk_id,
                event_id=event.id,
                user_id=event.user_id,
                risk_score=score,
                severity=severity,
                risk_factors=[f.model_dump(mode='json') for f in risk_factors],
                correlation_factors=[c.model_dump(mode='json') for c in correlation_factors],
                correlated_anomalies=[a.model_dump(mode='json') for a in normalized],
                explanation=explanation,
                scoring_version=settings.RISK_ENGINE_VERSION
            )
            db.add(record)
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                raise e
        
        return RiskAssessmentResponse(
            risk_id=risk_id,
            event_id=event.id,
            user_id=event.user_id,
            risk_score=score,
            severity=severity,
            risk_factors=risk_factors,
            correlation_factors=correlation_factors,
            correlated_anomalies=normalized,
            explanation=explanation,
            scoring_version=settings.RISK_ENGINE_VERSION
        )

risk_engine = RiskEngine()
