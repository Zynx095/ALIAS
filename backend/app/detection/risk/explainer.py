from typing import List
from schemas.risk import RiskFactor

class RiskExplainer:
    """Generates an explicit traceable explanation of the risk calculation."""
    
    @staticmethod
    def generate_explanation(score: float, severity: str, risk_factors: List[RiskFactor]) -> str:
        if not risk_factors:
            return "No anomalous behavior detected. Risk is baseline."
            
        lines = [f"Deterministic Risk Assessment: {score:.1f}/100 ({severity})", ""]
        lines.append("Contributing Factors:")
        
        # Sort factors by contribution descending
        sorted_factors = sorted(risk_factors, key=lambda f: f.contribution, reverse=True)
        
        for f in sorted_factors:
            lines.append(f"- {f.name} (+{f.contribution:.1f}): {f.description}")
            
        return "\n".join(lines)
