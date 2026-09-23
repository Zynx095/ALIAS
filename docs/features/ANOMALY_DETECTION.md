# Feature: Multi-Signal Anomaly Detection

## Metadata
- **Feature Name:** Multi-Signal Anomaly Detection
- **Status:** NOT IMPLEMENTED
- **Related Phase:** Phase 4 (Anomaly Detection)
- **Dependencies:** User Behavioral Profiling, Login Event Ingestion & Storage

---

## 1. Description
Evaluates incoming authentication events across multiple discrete threat dimensions (device, geography, time, frequency, IP reputation) comparing current event attributes against established user behavioral baselines.

---

## 2. Intended Behavior
- **Device Anomaly Detector:** Flags logins executed from an unrecognized browser, novel operating system, or completely new device type.
- **Geo-Velocity / Impossible Travel Detector:** Uses the Haversine equation to calculate the physical speed required to travel between the current login location and the preceding login location. Flags speeds exceeding standard commercial aviation thresholds (> 800 km/h).
- **Temporal Anomaly Detector:** Computes the probability of a login occurring at the given hour based on the user's historical active hour distribution, flagging sharp deviations (e.g., 3:00 AM access for a 9-to-5 employee).
- **Brute Force & Credential Spray Detector:** Tracks authentication failures within a sliding window. Differentiates single-user brute force attacks from multi-account password spray campaigns originating from single IP blocks.
- **IP Reputation Detector:** Identifies access originating from Tor exit nodes, public VPN/proxy providers, bulletproof hosting providers, or anomalous ASNs.
- **Output:** Emits structured `AnomalyRecord` instances detailing anomaly type, confidence score, raw deviation metrics, and timestamp.

---

## 3. Dependencies
- `backend/app/models/anomaly.py`
- `backend/app/schemas/anomaly.py`
- `backend/app/detection/base.py`
- Baseline profiles from `UserBaseline`
