# Phase 4: Anomaly Detection Engine

**STATUS: COMPLETE**

## Objective
Take factual behavioral deviations from Phase 3 and determine whether one or more explicitly defined behavioral anomaly conditions are present.

## Architecture
- **Location:** `backend/app/detection/anomalies/`
- **Detectors Implemented:**
  - `TemporalAnomalyDetector`
  - `DeviceAnomalyDetector`
  - `LocationAnomalyDetector` (includes Impossible Travel)
  - `NetworkAnomalyDetector`
  - `AuthenticationAnomalyDetector` (includes Failure Burst)
  - `AccessPatternAnomalyDetector`
- **Engine:** `AnomalyDetectionEngine` safely runs all detectors and deduplicates findings.
- **Persistence:** Findings are saved to SQLite in the `anomaly_records` table, now updated to store factual fields (detector, signal, feature, observed_value) instead of subjective `severity` or `score`.

## APIs
- `GET /api/events/{event_id}/anomalies`
- `POST /api/events/{event_id}/anomalies/evaluate`

## Websockets
The ingestion background task now automatically runs the anomaly engine and broadcasts a structured `ANOMALY_DETECTED` payload via `/ws/alerts`.

## Testing
- Unit tests for all detectors (`test_anomalies_detectors.py`).
- API/Scenario tests (`test_anomalies_api.py`) verifying end-to-end detection pipelines without regressions.

## Limitations & Boundaries
- No risk scores or severity levels are calculated.
- Anomalies are entirely factual (e.g. "User logged in from unseen device fingerprint").
- Phase 4 sets the foundation for Phase 5 to perform multi-signal correlation and risk scoring.
