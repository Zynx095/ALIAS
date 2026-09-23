"""Schemas for Anomaly Detection (Phase 4).

Strict Phase 4 Boundary: These schemas represent factual behavioral anomalies.
They DO NOT include risk scores, threat verdicts, or maliciousness levels.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class AnomalyType(str):
    TEMPORAL_ANOMALY = "TEMPORAL_ANOMALY"
    DEVICE_ANOMALY = "DEVICE_ANOMALY"
    LOCATION_ANOMALY = "LOCATION_ANOMALY"
    NETWORK_ANOMALY = "NETWORK_ANOMALY"
    AUTHENTICATION_ANOMALY = "AUTHENTICATION_ANOMALY"
    ACCESS_PATTERN_ANOMALY = "ACCESS_PATTERN_ANOMALY"


class AnomalyFinding(BaseModel):
    """A structured finding representing a single anomaly condition met."""
    anomaly_id: str
    event_id: int
    user_id: str
    anomaly_type: str
    detector: str
    signal: str
    feature: str
    observed_value: Optional[str] = None
    expected_state: Optional[str] = None
    evidence: Dict[str, Any] = Field(default_factory=dict)
    explanation: str
    baseline_version: Optional[str] = None
    rule_id: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)

    def generate_id(self) -> str:
        """Deterministic ID based on event and rule."""
        import hashlib
        key = f"{self.event_id}_{self.detector}_{self.rule_id}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]


class AnomalyDetectionResponse(BaseModel):
    """Response payload for anomaly evaluation endpoints."""
    event_id: int
    user_id: str
    baseline_version: Optional[str]
    anomalies: List[AnomalyFinding]
    detected_at: datetime
    has_anomalies: bool
