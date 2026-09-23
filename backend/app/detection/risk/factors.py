from typing import List, Dict, Any
from schemas.risk import NormalizedAnomaly, CorrelationFactor, RiskFactor
from core.config import get_settings

settings = get_settings()

class RiskFactorBuilder:
    """Builds RiskFactors by evaluating normalized anomalies and correlation factors."""
    
    @staticmethod
    def build_factors(normalized_anomalies: List[NormalizedAnomaly], correlation_factors: List[CorrelationFactor]) -> List[RiskFactor]:
        risk_factors = []
        
        # 1. Base Anomaly Contributions
        for anomaly in normalized_anomalies:
            weight = RiskFactorBuilder._get_base_weight(anomaly.signal)
            risk_factors.append(RiskFactor(
                factor_id=f"BASE_{anomaly.anomaly_type}",
                name=f"{anomaly.signal} Anomaly",
                description=f"Behavioral deviation detected in {anomaly.signal} dimension: {anomaly.feature}.",
                contribution=weight,
                supporting_anomalies=[anomaly.anomaly_id]
            ))
            
        # 2. Correlation Multipliers
        for corr in correlation_factors:
            contribution = 0.0
            if corr.factor_id == "MULTI_SIGNAL_SAME_EVENT":
                # Flat bump for having multiple signals
                contribution = 10.0
            elif corr.factor_id == "AUTH_FAILURE_BURST_THEN_SUCCESS":
                contribution = 20.0
            elif corr.factor_id == "NEW_DEVICE_NEW_LOCATION":
                contribution = 15.0
            elif corr.factor_id == "OFF_HOURS_MULTI_ANOMALY":
                contribution = 10.0
                
            if contribution > 0:
                risk_factors.append(RiskFactor(
                    factor_id=corr.factor_id,
                    name=corr.name,
                    description=corr.description,
                    contribution=contribution,
                    supporting_anomalies=corr.related_anomaly_ids
                ))
                
        return risk_factors

    @staticmethod
    def _get_base_weight(signal: str) -> float:
        weights = {
            "DEVICE": settings.WEIGHT_DEVICE,
            "LOCATION": settings.WEIGHT_LOCATION,
            "NETWORK": settings.WEIGHT_NETWORK,
            "TEMPORAL": settings.WEIGHT_TEMPORAL,
            "AUTHENTICATION": settings.WEIGHT_AUTH,
            "ACCESS_PATTERN": settings.WEIGHT_ACCESS
        }
        return weights.get(signal, 5.0)
