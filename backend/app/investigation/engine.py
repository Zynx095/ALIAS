"""Investigation Engine for AI-assisted forensic reporting."""
import logging
import hashlib
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.config import get_settings
from models.database import LoginEvent, AnomalyRecord, RiskAssessment, InvestigationReport
from investigation.providers import get_llm_provider

logger = logging.getLogger("alias.investigation.engine")

class InvestigationEngine:
    """Orchestrates evidence collection, LLM analysis, and DB persistence."""
    
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_llm_provider(get_settings())
        self.investigation_version = "investigation_v1"

    def _generate_investigation_id(self, event_id: int, version: str) -> str:
        """Deterministically generate an investigation ID based on event and version."""
        raw = f"{event_id}_{version}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _collect_evidence(self, event: LoginEvent) -> Dict[str, Any]:
        """Gather all deterministic evidence for the event."""
        # 1. Event Telemetry
        event_dict = {
            "event_id": event.id,
            "user_id": event.user_id,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "ip_address": event.ip_address,
            "location": event.location,
            "latitude": event.latitude,
            "longitude": event.longitude,
            "device_fingerprint": event.device_fingerprint,
            "user_agent": event.user_agent,
            "auth_status": event.auth_status,
            "failed_attempts": event.failed_attempts,
            "access_pattern": event.access_pattern
        }
        
        # 2. Anomalies
        anomalies = self.db.query(AnomalyRecord).filter(AnomalyRecord.event_id == event.id).all()
        anomalies_list = []
        for a in anomalies:
            anomalies_list.append({
                "anomaly_id": str(a.id),
                "signal": a.signal,
                "anomaly_type": a.anomaly_type,
                "detector": a.detector,
                "feature": a.feature,
                "observed_value": a.observed_value,
                "expected_state": a.expected_state,
                "explanation": a.explanation,
                "rule_id": a.rule_id
            })
            
        # 3. Risk Assessment
        risk_record = self.db.query(RiskAssessment).filter(RiskAssessment.event_id == event.id).first()
        risk_dict = {}
        if risk_record:
            risk_dict = {
                "risk_score": risk_record.risk_score,
                "severity": risk_record.severity,
                "scoring_version": risk_record.scoring_version,
                "explanation": risk_record.explanation,
                "risk_factors": risk_record.risk_factors
            }
            
        return {
            "event": event_dict,
            "anomalies": anomalies_list,
            "risk": risk_dict
        }

    def evaluate_and_persist(self, event: LoginEvent, force_reevaluate: bool = False) -> Optional[InvestigationReport]:
        """Assemble evidence, consult AI, and save the resulting report."""
        inv_id = self._generate_investigation_id(event.id, self.investigation_version)
        
        # 1. Check existing
        existing = self.db.query(InvestigationReport).filter(InvestigationReport.investigation_id == inv_id).first()
        if existing and not force_reevaluate:
            return existing
            
        # 2. Collect Evidence Context
        evidence_context = self._collect_evidence(event)
        
        # 3. Invoke LLM Provider
        logger.info(f"Generating investigation for Event {event.id} via {self.provider.provider_name}...")
        try:
            ai_result = self.provider.generate_investigation(evidence_context)
        except Exception as e:
            logger.error(f"Failed to generate investigation for Event {event.id}: {e}")
            return None
            
        # 4. Construct DB Model
        risk_data = evidence_context.get("risk", {})
        
        report = existing if existing else InvestigationReport()
        report.investigation_id = inv_id
        report.event_id = event.id
        report.user_id = event.user_id
        report.risk_score = risk_data.get("risk_score", 0.0)
        report.severity = risk_data.get("severity", "LOW")
        
        report.summary = ai_result.get("summary")
        report.attack_scenario = ai_result.get("attack_scenario")
        report.indicators = ai_result.get("indicators", [])
        report.recommendations = ai_result.get("recommendations", [])
        
        report.observed_evidence = evidence_context.get("event", {})
        report.correlated_factors = risk_data.get("risk_factors", [])
        report.supporting_anomaly_ids = [a.get("anomaly_id") for a in evidence_context.get("anomalies", [])]
        
        report.llm_provider = self.provider.provider_name
        report.llm_model = self.provider.model_name
        report.investigation_version = self.investigation_version

        # 5. Persist
        try:
            if not existing:
                self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report
        except IntegrityError:
            self.db.rollback()
            # If concurrent race condition occurred, just fetch it
            return self.db.query(InvestigationReport).filter(InvestigationReport.investigation_id == inv_id).first()
        except Exception as e:
            self.db.rollback()
            logger.error(f"DB persistence failed for InvestigationReport {inv_id}: {e}")
            return None
