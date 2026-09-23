# Phase 5: Multi-Signal Correlation & Risk Scoring

## Phase Metadata
- **Phase ID:** 5
- **Phase Name:** Multi-Signal Correlation & Risk Scoring
- **Status:** NOT STARTED
- **Started:** —
- **Completed:** —
- **Prerequisites:** Phase 4 (Anomaly Detection)

---

## 1. Objective & Intended Responsibility
Phase 5 implements the multi-signal correlation and composite risk scoring engine. Single isolated anomalies often result in alert fatigue; this phase unifies multiple anomaly indicators across sliding time windows into high-fidelity threat incidents.

### Scope of Responsibility:
1. **Sliding Time-Window Correlation:** Group individual `AnomalyRecord` instances by `user_id`, `ip_address`, or session within configurable windows (e.g., 15-minute, 1-hour, 24-hour buckets).
2. **Multi-Signal Correlation Rules:** Detect compounding indicators:
   - Example: Credential failure burst + Sudden geographical shift + Novel device fingerprint = Account Takeover Attempt.
   - Example: Off-hours login + Cloud hosting ASN + MFA bypass failure = Reconnaissance / Brute Force.
3. **Composite Risk Engine:** Calculate a unified risk score from 0 to 100 based on weighted signal combinations, frequency, and severity modifiers.
4. **Severity Classification:**
   - **Low (0–29):** Informational or minor single deviations.
   - **Medium (30–59):** Noteworthy single anomaly or dual weak signals.
   - **High (60–84):** Correlated multi-signal anomalies requiring analyst triage.
   - **Critical (85–100):** High-confidence account takeover or active breach in progress.
5. **Real-Time Alert Dispatch:** Dispatch alerts via WebSocket for events categorized as High or Critical severity.

---

## 2. Key Deliverables
- `CorrelationEngine` and `RiskEngine` implementations in `backend/app/detection/`.
- Configurable risk scoring matrix and rule sets.
- WebSocket alert publisher triggering on high-severity incidents.
- Unit tests covering complex multi-signal correlation scenarios.
