from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ScenarioMetadata(BaseModel):
    scenario_id: str
    scenario_name: str
    description: str
    expected_signals: List[str]
    expected_anomalies: List[str]
    expected_risk_range: str
    expected_investigation: bool
    events_generated: int

class ScenarioStatusResponse(BaseModel):
    status: str  # Ready, Running, Completed, Failed
    scenario_id: str
    message: Optional[str] = None
    events_generated: int = 0
    results: Optional[Dict[str, Any]] = None
