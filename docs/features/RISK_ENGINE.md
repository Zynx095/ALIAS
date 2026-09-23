# Feature: Risk Scoring & Severity Classification

## Metadata
- **Feature Name:** Risk Scoring & Severity Classification
- **Status:** NOT IMPLEMENTED
- **Related Phase:** Phase 5 (Multi-Signal Correlation & Risk Scoring)
- **Dependencies:** Multi-Signal Correlation Engine, Anomaly Detection

---

## 1. Description
Computes a normalized, composite threat risk score (0 to 100) for evaluated authentication attempts and correlated incidents, categorizing threats into standard security operations severity tiers.

---

## 2. Intended Behavior
- **Composite Scoring Formula:** Combines individual anomaly scores weighted by severity, frequency of occurrence, and user role criticality (e.g., Domain Admin accounts receive higher risk multiplier than standard user accounts).
  $$\text{Composite Score} = \min\left(100, \sum (w_i \times s_i) \times M_{\text{role}} \times M_{\text{frequency}}\right)$$
- **Severity Classification Tiers:**
  - **Low (0–29):** Minimal deviations; logged for trend analysis without analyst interruption.
  - **Medium (30–59):** Moderate single-factor deviation; logged in dashboard queue.
  - **High (60–84):** Significant multi-signal indicators; triggers instant alert notification.
  - **Critical (85–100):** High-confidence active threat or breach; triggers automated triage and instant WebSocket broadcast.
- **Action Triggers:** High and Critical risk classifications automatically trigger AI investigation dossier generation and real-time SOC alerts.

---

## 3. Dependencies
- `backend/app/detection/risk.py`
- `backend/app/schemas/anomaly.py`
- Configurable risk threshold weights in `Settings`
