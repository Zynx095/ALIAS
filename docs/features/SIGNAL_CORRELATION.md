# Feature: Multi-Signal Correlation Engine

## Metadata
- **Feature Name:** Multi-Signal Correlation Engine
- **Status:** NOT IMPLEMENTED
- **Related Phase:** Phase 5 (Multi-Signal Correlation & Risk Scoring)
- **Dependencies:** Multi-Signal Anomaly Detection, AnomalyRecord repository

---

## 1. Description
Aggregates and cross-correlates discrete anomaly signals occurring across users, sessions, network blocks, or sliding time windows. Transforms isolated low-priority anomalies into high-fidelity threat incidents.

---

## 2. Intended Behavior
- **Sliding Window Aggregation:** Maintains active correlation contexts (e.g., 15-minute, 1-hour, 24-hour windows) keyed by user ID, IP address, and tenant identifier.
- **Cross-Signal Rules Engine:** Identifies attack patterns formed by combining multiple distinct signals:
  - Pattern A: Rapid failed logins + Geo velocity jump + New device = High probability account takeover.
  - Pattern B: Off-hours login + Untrusted cloud ASN + MFA push fatigue = Session hijacking / Credential replay.
  - Pattern C: Identical User-Agent + 50 distinct user failures within 5 minutes = Distributed credential spray.
- **Incident Grouping:** Bundles related anomalies into a unified incident context to prevent SOC alert flooding.
- **Forwarding to Risk Engine:** Passes the correlated incident cluster to the Risk Scoring Engine for composite evaluation.

---

## 3. Dependencies
- `backend/app/detection/correlation.py`
- `backend/app/models/anomaly.py`
- Sliding window in-memory state or time-indexed database queries
