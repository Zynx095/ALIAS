from typing import List, Dict, Any
from schemas.risk import NormalizedAnomaly, CorrelationFactor
from schemas.anomalies import AnomalyFinding
from models.database import LoginEvent

class CorrelationEngine:
    """Correlates anomalies to find cross-signal patterns and contexts."""
    
    @staticmethod
    def evaluate(normalized_anomalies: List[NormalizedAnomaly], current_event: LoginEvent, recent_events: List[LoginEvent]) -> List[CorrelationFactor]:
        factors = []
        
        if not normalized_anomalies:
            return factors

        # 1. Multi-Signal (Same-Event) Correlation
        # If there are multiple distinct signals in the same event, that's a correlation factor.
        distinct_signals = set(a.signal for a in normalized_anomalies)
        if len(distinct_signals) > 1:
            factors.append(CorrelationFactor(
                factor_id="MULTI_SIGNAL_SAME_EVENT",
                name="Multi-Signal Event",
                description=f"Event triggered {len(distinct_signals)} distinct behavioral anomaly signals concurrently.",
                related_anomaly_ids=[a.anomaly_id for a in normalized_anomalies],
                context_data={"signals": list(distinct_signals)}
            ))

        # 2. Authentication Context
        # E.g., multiple failed attempts followed by a successful login.
        # recent_events is ordered by desc timestamp, and excludes current_event.
        if current_event.auth_status.upper() == "SUCCESS" and recent_events:
            failed_count = sum(1 for e in recent_events if e.auth_status.upper() == "FAILURE")
            if failed_count >= 3:
                # Get auth anomalies if any
                auth_anomalies = [a for a in normalized_anomalies if a.signal == "AUTHENTICATION"]
                factors.append(CorrelationFactor(
                    factor_id="AUTH_FAILURE_BURST_THEN_SUCCESS",
                    name="Success After Failure Burst",
                    description=f"A successful login occurred immediately after {failed_count} recent failures.",
                    related_anomaly_ids=[a.anomaly_id for a in auth_anomalies],
                    context_data={"recent_failures": failed_count}
                ))

        # 3. Behavioral Correlation (e.g. New Device + New Location)
        if "DEVICE" in distinct_signals and "LOCATION" in distinct_signals:
            related = [a.anomaly_id for a in normalized_anomalies if a.signal in ("DEVICE", "LOCATION")]
            factors.append(CorrelationFactor(
                factor_id="NEW_DEVICE_NEW_LOCATION",
                name="New Device in New Location",
                description="User logged in from an unseen device at an unseen geographic location simultaneously.",
                related_anomaly_ids=related,
                context_data={}
            ))
            
        # 4. Temporal Proximity (Correlation with recent anomalies is complex, for now we do event-level context)
        # If there's a temporal anomaly + anything else
        if "TEMPORAL" in distinct_signals and len(distinct_signals) > 1:
            related = [a.anomaly_id for a in normalized_anomalies]
            factors.append(CorrelationFactor(
                factor_id="OFF_HOURS_MULTI_ANOMALY",
                name="Off-Hours Multi-Anomaly",
                description="Multiple anomalies occurred outside of typical historical operating hours.",
                related_anomaly_ids=related,
                context_data={}
            ))

        return factors
