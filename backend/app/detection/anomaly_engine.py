"""Anomaly Detection Engine

STATUS: FOUNDATION ONLY — Interface definition only.
Actual detection algorithms will be implemented in Phase 4.

Responsibilities:
- Evaluate a login event against a user's behavioral baseline
- Detect: Device anomaly, Geo-velocity anomaly, Temporal anomaly,
  Brute-force anomaly, IP reputation anomaly
"""
from dataclasses import dataclass
import logging

logger = logging.getLogger("alias.detection.anomaly")


@dataclass
class AnomalyResult:
    """Structured result from a single anomaly check."""
    anomaly_type: str  # DEVICE, GEO_VELOCITY, TEMPORAL, BRUTE_FORCE, IP_REPUTATION
    detected: bool
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    score: float  # 0.0 – 1.0
    evidence: dict
    description: str


class AnomalyEngine:
    """Multi-signal anomaly detection engine.

    STATUS: FOUNDATION ONLY
    Detection algorithms will be implemented in Phase 4.
    """

    def evaluate(self, event: dict, baseline: dict | None) -> list[AnomalyResult]:
        """Evaluate a login event against the user's baseline.

        Args:
            event: LoginEvent data as a dictionary
            baseline: UserBaseline data as a dictionary, or None if no baseline exists

        Returns:
            List of AnomalyResult findings

        STATUS: NOT IMPLEMENTED
        """
        # TODO: Phase 4 — Implement detection algorithms:
        # - check_device_anomaly(event, baseline)
        # - check_geo_velocity(event, baseline)
        # - check_temporal_anomaly(event, baseline)
        # - check_brute_force(event, baseline)
        # - check_ip_reputation(event, baseline)
        logger.info(f"Anomaly evaluation requested — engine not yet implemented")
        return []
