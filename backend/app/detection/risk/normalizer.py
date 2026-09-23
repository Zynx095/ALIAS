from typing import List
from schemas.anomalies import AnomalyFinding
from schemas.risk import NormalizedAnomaly

class AnomalyNormalizer:
    """Normalizes Phase 4 anomalies into a simpler schema for Phase 5 correlation."""
    
    @staticmethod
    def normalize(anomalies: List[AnomalyFinding]) -> List[NormalizedAnomaly]:
        normalized = []
        for a in anomalies:
            normalized.append(NormalizedAnomaly(
                anomaly_id=a.anomaly_id,
                event_id=a.event_id,
                user_id=a.user_id,
                anomaly_type=a.anomaly_type,
                detector=a.detector,
                signal=a.signal,
                feature=a.feature,
                detected_at=a.detected_at
            ))
        return normalized
