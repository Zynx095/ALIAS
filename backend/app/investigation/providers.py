"""LLM Provider abstraction layer with isolated deterministic fallback."""
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger("alias.investigation.providers")

class BaseLLMProvider(ABC):
    """Abstract interface for investigation LLM providers."""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    def generate_investigation(self, evidence_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured investigation output given evidence context."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """Deterministic fallback provider requiring no external API keys or network calls."""
    
    @property
    def provider_name(self) -> str:
        return "mock-fallback"
        
    @property
    def model_name(self) -> str:
        return "rule-grounded-v1"

    def generate_investigation(self, evidence_context: Dict[str, Any]) -> Dict[str, Any]:
        event = evidence_context.get("event", {})
        anomalies = evidence_context.get("anomalies", [])
        risk = evidence_context.get("risk", {})
        
        user_id = event.get("user_id", "Unknown User")
        ip = event.get("ip_address", "Unknown IP")
        device = event.get("device_fingerprint", "Unknown Device")
        auth_status = event.get("auth_status", "SUCCESS")
        score = risk.get("risk_score", 0.0)
        severity = risk.get("severity", "LOW")
        
        # Grounded summary
        if score == 0.0 or not anomalies:
            summary = (
                f"Authentication attempt for user '{user_id}' from IP {ip} was evaluated as BENIGN with a risk score of {score:.1f} ({severity}). "
                f"No behavioral anomalies or deviations from user baseline were identified."
            )
            attack_scenario = (
                f"The login event aligns fully with normal historical activity for {user_id}. "
                f"Authentication succeeded with standard network and device parameters."
            )
            indicators = [f"ip:{ip}"]
            if device and device != "Unknown Device":
                indicators.append(f"device:{device}")
            recommendations = ["No action required. Activity is consistent with normal operations."]
        else:
            anomaly_types = [a.get("anomaly_type") for a in anomalies if a.get("anomaly_type")]
            summary = (
                f"Suspicious login activity detected for user '{user_id}' from IP {ip} yielding a risk score of {score:.1f} ({severity}). "
                f"Event triggered {len(anomalies)} behavioral anomaly signal(s): {', '.join(set(anomaly_types))}."
            )
            
            # Construct scenario from risk factors
            risk_factors = risk.get("risk_factors", [])
            factor_names = [rf.get("name") for rf in risk_factors if rf.get("name")]
            scenario_text = (
                f"Anomalous authentication observed for {user_id} with status {auth_status}. "
                f"Primary risk drivers include: {'; '.join(factor_names) if factor_names else 'detected baseline deviations'}. "
            )
            if "AUTHENTICATION" in [a.get("signal") for a in anomalies]:
                scenario_text += "A spike in previous authentication failures suggests potential credential brute-force or spraying prior to access. "
            if "LOCATION" in [a.get("signal") for a in anomalies] or "DEVICE" in [a.get("signal") for a in anomalies]:
                scenario_text += "Session originates from an atypical device or geographic origin compared to historical baseline. "
                
            attack_scenario = scenario_text.strip()
            
            # Extract IoCs from evidence
            indicators = [f"ip:{ip}"]
            if device and device != "Unknown Device":
                indicators.append(f"device:{device}")
            for a in anomalies:
                if a.get("rule_id"):
                    indicators.append(f"rule:{a.get('rule_id')}")
            indicators = list(dict.fromkeys(indicators))  # Deduplicate preserving order
            
            # Tailor recommendations by severity
            if severity in ("HIGH", "CRITICAL"):
                recommendations = [
                    f"Immediately verify session legitimacy with user '{user_id}'.",
                    f"Consider temporary credential reset or session revocation for user '{user_id}'.",
                    f"Audit secondary authentication logs for IP {ip}.",
                    f"Place IP {ip} on watchlist for subsequent authentication attempts."
                ]
            else:
                recommendations = [
                    f"Monitor user '{user_id}' for follow-on anomalous activity.",
                    f"Review device registration for {device} if user confirmed device upgrade."
                ]
                
        return {
            "summary": summary,
            "attack_scenario": attack_scenario,
            "indicators": indicators,
            "recommendations": recommendations
        }


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI API Provider with automatic fallback to MockLLMProvider."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self._model_name = model_name or "gpt-4o-mini"
        self.fallback = MockLLMProvider()

    @property
    def provider_name(self) -> str:
        return "openai"
        
    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_investigation(self, evidence_context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("OpenAI API key missing. Falling back to MockLLMProvider.")
            return self.fallback.generate_investigation(evidence_context)
            
        try:
            import urllib.request
            from investigation.prompt import InvestigationPromptBuilder
            
            sys_prompt = InvestigationPromptBuilder.SYSTEM_PROMPT
            user_prompt = InvestigationPromptBuilder.build_user_prompt(evidence_context)
            
            payload = {
                "model": self._model_name,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return parsed
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}. Falling back to MockLLMProvider.")
            return self.fallback.generate_investigation(evidence_context)


class GeminiLLMProvider(BaseLLMProvider):
    """Gemini API Provider with automatic fallback to MockLLMProvider."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self._model_name = model_name or "gemini-1.5-flash"
        self.fallback = MockLLMProvider()

    @property
    def provider_name(self) -> str:
        return "gemini"
        
    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_investigation(self, evidence_context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("Gemini API key missing. Falling back to MockLLMProvider.")
            return self.fallback.generate_investigation(evidence_context)
            
        try:
            import urllib.request
            from investigation.prompt import InvestigationPromptBuilder
            
            sys_prompt = InvestigationPromptBuilder.SYSTEM_PROMPT
            user_prompt = InvestigationPromptBuilder.build_user_prompt(evidence_context)
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{sys_prompt}\n\n{user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2
                }
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(content)
                return parsed
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}. Falling back to MockLLMProvider.")
            return self.fallback.generate_investigation(evidence_context)


def get_llm_provider(settings) -> BaseLLMProvider:
    """Factory function to instantiate the configured LLM provider."""
    provider_type = (settings.LLM_PROVIDER or "none").lower()
    
    if provider_type in ("openai", "gpt"):
        return OpenAILLMProvider(api_key=settings.LLM_API_KEY, model_name=settings.LLM_MODEL)
    elif provider_type in ("gemini", "google"):
        return GeminiLLMProvider(api_key=settings.LLM_API_KEY, model_name=settings.LLM_MODEL)
    else:
        return MockLLMProvider()
