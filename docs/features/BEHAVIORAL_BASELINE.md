# Feature: User Behavioral Profiling

## Metadata
- **Feature Name:** User Behavioral Profiling
- **Status:** COMPLETE
- **Related Phase:** Phase 3 (Behavioral Baseline Engine)
- **Dependencies:** Login Event Ingestion & Storage, SQLite `user_baselines` table

---

## 1. Description
Maintains a statistical representation of normal user behavior derived from historical authentication activity. The baseline serves as the reference against which new authentication attempts are evaluated to spot anomalies.

---

## 2. Intended Behavior
- **Profile Construction:** Aggregates historical login events to calculate behavioral metrics across 6 canonical dimensions:
  - **Temporal Profile:** Hourly distribution of logins, typical workday patterns vs. weekend activity.
  - **Device Profile:** List of verified device fingerprints.
  - **Location Profile:** List of known locations and coordinates.
  - **Network Profile:** Known IPs, CIDR subnets (/24, /64), and IP protocol versions.
  - **Authentication Profile:** Attempt counts, failure rates, and outcome distributions.
  - **Access Pattern Profile:** Known routing mechanisms (DIRECT, VPN, TOR).
- **Lifecycle & Update Strategy:** Baselines track versions (deterministic SHA-256) and handle cold starts via strict states (`NO_BASELINE`, `INSUFFICIENT_HISTORY`, `READY`). The system does NOT automatically update the baseline to prevent contamination—it leverages an explicit rebuild process via `/api/users/{user_id}/baseline/rebuild`.
- **Baseline Comparison Interface:** Exposes objective deviation evidence to the WebSocket layer (`BEHAVIORAL_COMPARISON`) and to analysts via `/api/events/{event_id}/behavioral-comparison`.

---

## 3. Dependencies
- `backend/app/models/baseline.py`
- `backend/app/schemas/baseline.py`
- `backend/app/services/baseline_service.py`
- Historical authentication events in `login_events` table
