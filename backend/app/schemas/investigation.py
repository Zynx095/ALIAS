"""Investigation and AI report schemas (Phase 6)."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class InvestigationReportResponse(BaseModel):
    """Schema for a complete AI-assisted investigation report."""
    investigation_id: str
    event_id: int
    user_id: str
    risk_score: float
    severity: str
    summary: str
    attack_scenario: str
    indicators: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    observed_evidence: Dict[str, Any] = Field(default_factory=dict)
    correlated_factors: List[Dict[str, Any]] = Field(default_factory=list)
    supporting_anomaly_ids: List[str] = Field(default_factory=list)
    llm_provider: str
    llm_model: str
    investigation_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}

class InvestigationRequest(BaseModel):
    """Request schema for manually triggering an event investigation."""
    force_reevaluate: bool = False
