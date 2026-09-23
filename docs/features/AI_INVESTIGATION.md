# Feature: LLM-Assisted Forensic Investigation

## Metadata
- **Feature Name:** LLM-Assisted Forensic Investigation
- **Status:** NOT IMPLEMENTED
- **Related Phase:** Phase 6 (AI-Assisted Investigation)
- **Dependencies:** Multi-Signal Correlation & Risk Scoring, LLM Provider / Heuristic Engine

---

## 1. Description
Acts as an automated Level-1/Level-2 security analyst. When high-severity anomalies or correlated threat incidents occur, the AI investigator synthesizes authentication telemetry, baseline variance, and network intelligence into an explainable, structured forensic investigation dossier.

---

## 2. Intended Behavior
- **Contextual Synthesis:** Assembles chronological event logs, user baseline expectations, network metadata, and matched anomaly signals into a structured LLM prompt.
- **Dossier Generation:** Produces a standardized forensic report containing:
  - **Narrative Summary:** Clear, concise explanation of the incident timeline and anomalous behavior.
  - **MITRE ATT&CK Mapping:** Identifies applicable techniques (e.g., T1078 Valid Accounts, T1110 Brute Force, T1071 Application Layer Protocol).
  - **Hypothesis & Confidence Assessment:** Evaluates attack probability vs. false positive scenarios (e.g., corporate travel, new phone purchase).
  - **Actionable Remediation Checklist:** Prescribes concrete containment and eradication actions (e.g., terminate active sessions, reset credentials, revoke refresh tokens, block IP range).
- **Deterministic Heuristic Fallback:** If the LLM provider is unavailable or unconfigured, ALIAS falls back to a deterministic, rule-based template generator ensuring zero disruption to SOC operations.
- **Persistence & Audit Trail:** Saves all generated dossiers as `InvestigationReport` database entities.

---

## 3. Dependencies
- `backend/app/models/investigation.py`
- `backend/app/schemas/investigation.py`
- `backend/app/services/investigation_service.py`
- External LLM API or local inference server (optional/configurable)
