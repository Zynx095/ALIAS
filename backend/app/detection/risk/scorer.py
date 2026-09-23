from typing import List
from schemas.risk import RiskFactor

class RiskScorer:
    """Calculates a deterministic risk score bounded between 0 and 100."""
    
    @staticmethod
    def calculate_score(risk_factors: List[RiskFactor]) -> float:
        """Sum the contributions and clamp between 0.0 and 100.0."""
        total_score = sum(f.contribution for f in risk_factors)
        return max(0.0, min(100.0, total_score))
