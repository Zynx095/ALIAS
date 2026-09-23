# Phase 5: Multi-Signal Correlation & Contextual Risk Engine

**STATUS: COMPLETE**

## Objective
Consume the objective `AnomalyRecords` generated in Phase 4 and correlate them contextually to generate a deterministic `RiskAssessment`. Identify related behavior, calculate explainable risk scores (0-100), classify severities, and persist the outcome idempotently without relying on external LLMs or APIs.

## Architecture
- **Location:** `backend/app/detection/risk/`
- **Components Implemented:**
  - `normalizer.py`: Transforms DB models into memory schemas (`NormalizedAnomaly`).
  - `correlation.py`: Groups anomalies by temporal and entity relationships, finding cross-signal contexts (e.g., Auth burst followed by success, or New Device + New Location).
  - `factors.py`: Maps anomalies and correlation contexts into explicit, explainable `RiskFactors`.
  - `scorer.py`: Applies configurable base weights and context multipliers to the `RiskFactors`, capping the score at 100.
  - `severity.py`: Maps score to LOW, MODERATE, HIGH, or CRITICAL.
  - `explainer.py`: Generates deterministic traceability text.
  - `engine.py`: Central orchestration.
- **Persistence:** Saved to `risk_assessments` table, keyed deterministically via SHA256(event_id + scoring_version).

## Formulas and Weights
Base Weights (from `core/config.py`):
- `DEVICE = 15.0`
- `LOCATION = 20.0`
- `NETWORK = 10.0`
- `TEMPORAL = 5.0`
- `AUTHENTICATION = 25.0`
- `ACCESS_PATTERN = 15.0`

Context Multipliers:
- `MULTI_SIGNAL_SAME_EVENT`: +10.0
- `AUTH_FAILURE_BURST_THEN_SUCCESS`: +20.0
- `NEW_DEVICE_NEW_LOCATION`: +15.0
- `OFF_HOURS_MULTI_ANOMALY`: +10.0

**Score = MIN(100.0, SUM(Base Weights) + SUM(Context Multipliers))**

Severities:
- `0-24`: LOW
- `25-49`: MODERATE
- `50-74`: HIGH
- `75-100`: CRITICAL

## APIs
- `GET /api/events/{event_id}/risk`
- `POST /api/events/{event_id}/risk/evaluate`

## Websockets
The ingestion background task now automatically runs the risk engine and broadcasts a structured `RISK_ASSESSMENT` payload via `/ws/alerts`.

## Limitations & Boundaries
- Deterministic scoring, NOT an LLM generation.
- Cannot block accounts (out of scope).
- External reputation APIs (VirusTotal, IP ranges) are NOT integrated.
- Explanations are factual combinations, not natural language paragraphs (Phase 6 handles the AI investigator).
