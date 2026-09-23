"""Prompt builder for LLM investigation grounding."""
from typing import Dict, Any, List

class InvestigationPromptBuilder:
    """Builds structured system and user prompts grounded strictly in DB evidence."""
    
    SYSTEM_PROMPT = (
        "You are an expert Cybersecurity Incident Response Analyst for ALIAS (AI-assisted Login Anomaly Investigation System).\n"
        "Your task is to analyze the provided evidence for a login event and generate a forensic investigation report.\n"
        "STRICT GUIDELINES:\n"
        "1. DO NOT invent or assume raw facts (such as external threat intelligence, IP owner names, or unprovided metadata) not contained in the evidence.\n"
        "2. Ground your summary, attack scenario, indicators of compromise, and recommendations ONLY in the provided event telemetry, detected anomalies, and correlated risk factors.\n"
        "3. Provide a clear, professional SOC forensic narration.\n"
        "4. Respond ONLY with a valid JSON object matching the requested schema.\n"
    )

    @staticmethod
    def build_user_prompt(evidence_context: Dict[str, Any]) -> str:
        event = evidence_context.get("event", {})
        anomalies = evidence_context.get("anomalies", [])
        risk = evidence_context.get("risk", {})
        
        prompt = (
            f"=== EVIDENTIARY CONTEXT FOR INVESTIGATION ===\n\n"
            f"--- 1. EVENT TELEMETRY ---\n"
            f"Event ID: {event.get('event_id')}\n"
            f"User ID: {event.get('user_id')}\n"
            f"Timestamp: {event.get('timestamp')}\n"
            f"IP Address: {event.get('ip_address')}\n"
            f"Location: {event.get('location')} (Lat: {event.get('latitude')}, Lon: {event.get('longitude')})\n"
            f"Device Fingerprint: {event.get('device_fingerprint')}\n"
            f"User Agent: {event.get('user_agent')}\n"
            f"Auth Status: {event.get('auth_status')}\n"
            f"Failed Attempts: {event.get('failed_attempts')}\n"
            f"Access Pattern: {event.get('access_pattern')}\n\n"
            
            f"--- 2. DETECTED BEHAVIORAL ANOMALIES ({len(anomalies)}) ---\n"
        )
        
        if not anomalies:
            prompt += "No behavioral anomalies detected for this event.\n\n"
        else:
            for idx, a in enumerate(anomalies, 1):
                prompt += (
                    f"Anomaly {idx}:\n"
                    f"  ID: {a.get('anomaly_id')}\n"
                    f"  Signal: {a.get('signal')} | Type: {a.get('anomaly_type')}\n"
                    f"  Detector: {a.get('detector')} | Feature: {a.get('feature')}\n"
                    f"  Observed Value: {a.get('observed_value')}\n"
                    f"  Expected State: {a.get('expected_state')}\n"
                    f"  Explanation: {a.get('explanation')}\n\n"
                )
                
        prompt += (
            f"--- 3. RISK ASSESSMENT & CORRELATION ---\n"
            f"Risk Score: {risk.get('risk_score')}/100\n"
            f"Severity: {risk.get('severity')}\n"
            f"Scoring Version: {risk.get('scoring_version')}\n"
            f"Risk Explanation: {risk.get('explanation')}\n\n"
            f"Risk Factors:\n"
        )
        
        risk_factors = risk.get("risk_factors", [])
        if not risk_factors:
            prompt += "  - None\n"
        else:
            for rf in risk_factors:
                prompt += f"  - {rf.get('name')} (+{rf.get('contribution')}): {rf.get('description')}\n"

        prompt += (
            "\n--- REQUIRED JSON RESPONSE FORMAT ---\n"
            "Return a JSON object with EXACTLY these keys:\n"
            "{\n"
            '  "summary": "<Concise 2-3 sentence executive forensic summary>",\n'
            '  "attack_scenario": "<Narrative hypothesis detailing how the evidence and anomalies align or if it appears benign>",\n'
            '  "indicators": ["<List of specific IoCs extracted from the evidence, e.g. IP, device fingerprint, anomaly rules>"],\n'
            '  "recommendations": ["<List of concrete, actionable SOC remediation or monitoring steps>"]\n'
            "}\n"
        )
        return prompt
