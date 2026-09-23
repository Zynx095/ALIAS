# Phase 3: Behavioral Baseline Engine

## Phase Metadata
- **Phase ID:** 3
- **Phase Name:** Behavioral Baseline Engine
- **Status:** COMPLETE
- **Started:** 2026-09-21
- **Completed:** 2026-09-21
- **Prerequisites:** Phase 2 (Ingestion Pipeline & Baseline Data)

---

## 1. Objective & Intended Responsibility
Phase 3 builds the behavioral profiling and comparison foundation that aggregates historical authentication telemetry into individual user behavioral baselines, defining "normal" behavior for each user identity and generating structured, factual deviation evidence. It also implements the lifecycle logic (versioning, cold starts) and API/WebSocket integration for this baseline data.

### Completed Modules (3.1 - 3.16):
1. **3.1 Baseline Profile Engine:** Master orchestrator compiling all behavioral models (`engine.py`).
2. **3.2 Temporal Behavior Model:** Hourly distributions, workday vs. weekend patterns, typical hours (`temporal_model.py`).
3. **3.3 Device Behavior Model:** Device fingerprints, usage counts, primary devices (`device_model.py`).
4. **3.4 Location Behavior Model:** Geographic hubs, coordinates, primary locations (`location_model.py`).
5. **3.5 Network/IP Behavior Model (Extended):** Known IPs, CIDR subnets (/24, /64), IP protocol versions (`network_model.py`).
6. **3.6 Authentication Behavior Model:** Total attempts, success/failure counts, failure rate, failed attempts (`auth_model.py`).
7. **3.7 Access Pattern Model:** Routing modes (DIRECT, VPN, TOR), frequency distributions (`access_model.py`).
8. **3.8 Behavioral Feature Extraction:** Standardized per-event feature extraction (`feature_extractor.py`).
9. **3.9 Baseline Comparison Engine:** Mathematical delta computation across all 6 dimensions (`comparison_engine.py`).
10. **3.10 Deviation Evidence:** Structured, human-readable, factual evidence generation (`deviation_evidence.py`).
11. **3.11 Baseline Versioning:** Deterministic SHA-256 canonical hashing for baseline state (`schemas/baseline.py`).
12. **3.12 Cold-Start Handling:** `BaselineStatus` states (NO_BASELINE, INSUFFICIENT_HISTORY, READY) preventing false positive deviations (`engine.py`).
13. **3.13 Update Policy:** Manual, controlled baseline rebuilds instead of automatic rolling updates upon ingestion.
14. **3.14 API Integration:** REST endpoints for `GET /baseline`, `POST /baseline/rebuild`, and `POST /behavioral-comparison`.
15. **3.15 WebSocket Integration:** Asynchronous broadcast of `BEHAVIORAL_COMPARISON` events.
16. **3.16 Testing:** Comprehensive test suite with 36/36 tests passing cleanly.

### Strict Phase Boundary:
- No anomaly scoring or security verdicts.
- No risk scores or severity ratings.
- No LLM / AI calls.

---

## 2. Key Deliverables & Test Verification
- All 6 behavioral models implemented and integrated into `BaselineProfileEngine`.
- `BehavioralFeatureExtractor`, `BaselineComparisonEngine`, and `DeviationEvidenceBuilder` active.
- Database `user_baselines` updated with `auth_profile` and `access_patterns`.
- 34/34 tests passing cleanly (6 unit tests, 28 integration tests).
