"""Schemas for Multi-Signal Correlation and Contextual Risk Engine (Phase 5)."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from schemas.anomalies import AnomalyFinding

class NormalizedAnomaly(BaseModel):
    """Normalized representation of a Phase 4 AnomalyFinding for correlation."""
    anomaly_id: str
    event_id: int
    user_id: str
    anomaly_type: str
    detector: str
    signal: str
    feature: str
    detected_at: datetime

class CorrelationFactor(BaseModel):
    """A deterministic correlation rule that fired."""
    factor_id: str
    name: str
    description: str
    related_anomaly_ids: List[str]
    context_data: Dict[str, Any] = Field(default_factory=dict)

class RiskFactor(BaseModel):
    """An explainable factor contributing to the final risk score."""
    factor_id: str
    name: str
    description: str
    contribution: float
    supporting_anomalies: List[str]
    
class RiskAssessmentResponse(BaseModel):
    """The canonical deterministic risk assessment for an event."""
    risk_id: str
    event_id: int
    user_id: str
    risk_score: float
    severity: str
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    correlation_factors: List[CorrelationFactor] = Field(default_factory=list)
    correlated_anomalies: List[NormalizedAnomaly] = Field(default_factory=list)
    explanation: str
    scoring_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
