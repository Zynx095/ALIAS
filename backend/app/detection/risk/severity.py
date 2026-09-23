from core.config import get_settings

settings = get_settings()

class SeverityClassifier:
    """Maps a risk score to a deterministic severity classification."""
    
    @staticmethod
    def classify(score: float) -> str:
        if score < settings.SEVERITY_MODERATE:
            return "LOW"
        elif score < settings.SEVERITY_HIGH:
            return "MODERATE"
        elif score < settings.SEVERITY_CRITICAL:
            return "HIGH"
        else:
            return "CRITICAL"
