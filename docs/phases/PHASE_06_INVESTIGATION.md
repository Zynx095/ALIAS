# Phase 6: AI-Assisted Investigation

## Phase Metadata
- **Phase ID:** 6
- **Phase Name:** AI-Assisted Investigation
- **Status:** NOT STARTED
- **Started:** —
- **Completed:** —
- **Prerequisites:** Phase 5 (Multi-Signal Correlation & Risk Scoring)

---

## 1. Objective & Intended Responsibility
Phase 6 builds the AI-driven forensic investigation layer of ALIAS. Instead of leaving raw anomalies to manual analysis, ALIAS orchestrates an LLM forensic analyst that generates structured, explainable investigation dossiers.

### Scope of Responsibility:
1. **Forensic Context Assembly:** Aggregate raw login events, historical baseline deviations, correlated anomaly signals, and network intelligence into a structured investigative prompt.
2. **LLM Orchestration:** Interface with LLM providers (e.g., OpenAI API or local LLM runtimes) with structured schema outputs:
   - **Executive Summary:** Plain-English narrative explaining the timeline and nature of the anomaly.
   - **MITRE ATT&CK Mapping:** Map findings to standard tactics and techniques (e.g., T1078 Valid Accounts, T1110 Brute Force, T1090 Proxy).
   - **Confidence Score & Reasoning:** Explainable justification for why this activity is malicious vs. benign.
   - **Recommended Remediations:** Specific tactical steps (e.g., terminate active session, force password change, enroll in hardware token, block source subnet).
3. **Deterministic Fallback Explainer:** Provide a rule-based forensic generator to ensure system operation when LLM connectivity is unavailable.
4. **Investigation Lifecycle Management:** Enable SOC analysts to review, adjust status (Open, Investigating, Resolved, False Positive), and export investigation reports.

---

## 2. Key Deliverables
- `InvestigationService` and AI investigator agent module.
- Structured Pydantic validation for LLM outputs.
- Deterministic heuristic fallback engine.
- Report persistence and status update REST endpoints (`/api/v1/investigations`).
