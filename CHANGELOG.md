# ALIAS — Changelog

All notable changes to the ALIAS project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [R8.1] - 2026-09-23 (frontend, uncommitted)

### Investigated
- Reported: Impossible Travel (Scenario 3) appeared to remain "Running" indefinitely in the actual frontend. Reproduced the exact realistic usage pattern (one persistent WebSocket connection, scenarios run in sequence, exactly like `AlertContext`) against a live backend, and separately replayed the real captured message sequence through the exact `AlertContext`/`ScenarioConsole` reducer logic (Node, not React, to isolate pure logic from DOM/browser timing). Both independently confirmed: target-event selection (last `event_id`), WebSocket message delivery, and the completion-detection gate are all correct — `isTargetEventComplete` returns `true` at the exact point `INVESTIGATION_REPORT` arrives, matching design. Could not reproduce the reported hang through any test available without a browser.
- Found one real, provable-by-construction gap during the audit: `AlertContext`'s WebSocket reconnect logic (`setTimeout(connect, 3000)` on close) has no backlog/replay — any message broadcast during a disconnect window is permanently lost, and nothing re-checks state afterward. A scenario "running" across such a gap would wait forever for a signal that already fired. This isn't proven to be the actual cause of the reported hang (no browser access to confirm), but it's a real structural gap, and multi-event scenarios like Impossible Travel have a longer processing window, making them statistically more likely to span a drop.

### Fixed
- `ScenarioConsole.jsx`: added a reconnect-resync effect — when `connectionStatus` transitions back to `'connected'`, any scenario still shown as `'running'` is resynced directly via the existing REST endpoints (`fetchEventRisk`, `fetchInvestigation` — the same ones `InvestigationWorkspace` already uses), not a timer, not a guess. If the REST state shows the pipeline actually finished, the run is marked completed from that real data; if not yet available (404), it's left as `'running'` — no fabricated failure state introduced.
- No `setTimeout` anywhere marks a run `'completed'` or `'failed'` — verified by grep; the only timers in the file are the cosmetic terminal-state auto-clear (already existed in R8) and the Reset-button arm countdown, neither of which fabricates a pipeline result.

### Verified
- All 5 canonical scenarios re-run against a live backend after the fix, on a single persistent connection: identical results to the R8 baseline (Normal Login 0/LOW, New Device 15/LOW, Impossible Travel 40/MODERATE, Auth Burst 45/MODERATE, Multi-Signal 90/CRITICAL) — no regression.
- Backend: 61/61, 3 repeated runs.
- **Not claiming the browser-observed hang is fixed** — I cannot demonstrate that without browser access to reproduce the original symptom. The resync fix closes a real, verified architectural gap; whether it was the actual trigger for what was seen remains unconfirmed.

## [R8] - 2026-09-23 (frontend, uncommitted)

### Fixed
- `ScenarioConsole.jsx` marked a scenario run "Completed" the instant `POST /api/scenarios/{id}/run` returned HTTP 200 — but that endpoint always returns `status: "Running"` synchronously while the real pipeline (behavioral comparison → anomaly detection → risk → investigation) continues via `BackgroundTasks`. The "Completed" state was therefore fake: it reflected "the request was accepted," not "the pipeline finished." Rewrote completion detection to watch the existing `AlertContext` WebSocket pipeline state for the scenario's target event, gated on the actual backend broadcast contract verified directly from `backend/app/api/events.py`: `RISK_ASSESSMENT` is broadcast unconditionally for every event; `ANOMALY_DETECTED` only when anomalies exist (so a scenario like Normal Login legitimately never sends one — completion must not wait on it); `INVESTIGATION_REPORT` only when `risk_score > 0`.
- Console never exposed the resulting event/investigation. Added an "Open Investigation" action on completion, wired through the existing R6/R7 navigation (`onOpenInvestigation`), preserving origin-aware Back behavior (Scenario Console lives on Overview, so Back correctly returns to Overview).
- Reset Demo cleared backend demo data but left the frontend's locally-accumulated WebSocket stream/KPI counts showing already-deleted events. `AlertContext` gained a `clearStream()` method (clears local state only, does not touch the WebSocket connection); Reset now calls it after a successful backend reset. Reset also now requires a second confirming click ("Reset Demo" → "Confirm Reset?") before running, since it is destructive.
- Centralized scenario/reset API calls into `services/api.js` (`fetchScenarios`, `runScenario`, `resetDemo`) — `ScenarioConsole.jsx` previously called `fetch()` directly, inconsistent with the rest of the app.
- Corrected `docs/demo/runbook.md`'s "New Device: Risk Score: Medium" claim — verified against a live, freshly-reset backend run (see report) that this scenario deterministically produces `risk_score=15.0`, `severity=LOW` (single `DEVICE` anomaly, base weight 15, no correlation modifiers), not "Medium."

### Verified (live backend, not just static review)
- Started the real backend and ran all 5 canonical scenarios against a real WebSocket listener, confirming the exact lifecycle and payloads for each: Normal Login terminates at `RISK_ASSESSMENT` (score 0, no `ANOMALY_DETECTED`/`INVESTIGATION_REPORT` — correctly expected); New Device, Impossible Travel, Auth Burst, and Multi-Signal all produce the full `LOGIN_EVENT → BEHAVIORAL_COMPARISON → ANOMALY_DETECTED → RISK_ASSESSMENT → INVESTIGATION_REPORT` chain. Confirmed New Device's risk score is deterministic across a reset+rerun (15.0/LOW both times).
- Backend test suite: 61/61, 3 repeated runs, unaffected (no backend files changed).

## [0.10.0] - 2026-09-23

### Fixed
- Cross-module test infrastructure isolation, root-caused after the Phase 9 fix exposed 2 investigation-test failures and a 20-failed/41-passed full-suite result. Two distinct causes, both test-only:
  1. `tests/api/test_events.py` set `app.dependency_overrides[get_db]` to its own isolated `test_events.db` at module import time and never restored it, silently redirecting every other test file's DB access to a different SQLite file for the rest of the pytest session. Removed the custom engine/override/fixture block; the file now relies on the shared override already provided by `tests/conftest.py`.
  2. `tests/api/test_anomalies_api.py`, `tests/api/test_baseline_api.py`, and `tests/api/test_risk_scenarios.py` each had an autouse fixture that called `Base.metadata.drop_all(bind=engine)` in teardown. Since `engine` (imported from `models.database`) resolves to the same `test_alias.db` used by `conftest.py`'s session-scoped `test_engine`, this dropped the shared schema after each of these single-test modules ran, breaking every test that ran afterward (`no such table: investigation_reports`, etc.). Removed the destructive create/drop calls; schema lifecycle is now solely owned by `conftest.py`.
- No production code changed (API, WebSocket, anomaly detection, baseline, risk scoring, and investigation logic untouched).
- Verified: full backend suite (`tests/`) passes 61/61, confirmed across 3 repeated full runs and back-to-back runs without deleting the test database between them. `tests/api/test_scenarios.py` (Phase 9) independently reconfirmed 7/7, unaffected by this fix.
- Verified: no test execution wrote to the development database (`shadow_guard.db`); no `alias.db` or `test_events.db` file is produced anymore.

## [0.9.0] - 2026-09-23

### Fixed
- Phase 9 test bug: `test_run_new_device`, `test_run_impossible_travel`, and `test_run_auth_burst` in `tests/api/test_scenarios.py` asserted `status == 'success'`, but `POST /api/scenarios/{id}/run` intentionally returns `status="Running"` immediately (processing continues via `BackgroundTasks`), matching the behavior already correctly asserted by `test_run_normal_login` and `test_run_multi_signal` in the same file. Corrected the three assertions to `'Running'`. No production code changed.
- Verified: Phase 9 scenario suite (7/7) now passes reliably across repeated isolated runs and alongside `test_scenario_playback`, anomaly API tests, and risk scenario tests.
- Verified: no test execution wrote to the development database (`shadow_guard.db`); tests remain isolated to `test_alias.db` per `tests/conftest.py`.
- Known, pre-existing, out-of-scope issue: running the entire `tests/` suite together (not just the Phase 9/related matrix) still surfaces cross-module SQLite session/locking failures in unrelated modules (`test_events.py`, `test_integration.py` batch/history tests, `test_investigation_api.py`, `test_investigation_engine.py`). Confirmed present before this fix via `git stash` comparison; not addressed here per task scope.

## [0.8.0] - 2026-09-23

### Added
- Phase 8: SOC Dashboard.
- Completely refactored `App.jsx` from a legacy chat interface into a modular React SOC Dashboard.
- Implemented `AlertContext` for `ws/alerts` pipeline aggregation (LOGIN_EVENT -> ... -> INVESTIGATION_REPORT).
- Added `LiveStream` event feed component with chronological progression indicators and severity filtering.
- Added `InvestigationDetail` view enforcing evidence hierarchy (Fact -> Finding -> Risk -> AI).
- Integrated `react-globe.gl` dynamically to plot geographic telemetry directly from WebSocket login streams.
- Configured Vitest test suite and built synthetic E2E testing script `scripts/trigger_synthetic_login.py`.

## [0.7.0] - 2026-09-23

### Added
- Phase 7: API & WebSocket Integration.
- Finalized real-time `ws/alerts` WebSocket structure ensuring chronological dispatch (`LOGIN_EVENT` -> `BEHAVIORAL_COMPARISON` -> `ANOMALY_DETECTED` -> `RISK_ASSESSMENT` -> `INVESTIGATION_REPORT`).
- Validated ALIAS Idempotency guarantees (`source_event_id` checking).
- Dropped legacy endpoints and cleaned API router tree.
- Comprehensive `test_canonical_pipeline.py` covering E2E payload behavior and WS order.

## [0.6.0] - 2026-09-22

### Added
- Phase 6: AI-Assisted Investigation.
- Expanded `InvestigationReport` DB schema with evidence and tracking fields.
- `InvestigationEngine` and `InvestigationPromptBuilder` integrating structured prompt grounding.
- Pluggable `BaseLLMProvider` architecture with implementations for OpenAI and Gemini.
- `MockLLMProvider` for deterministic fallback offline functionality.
- Real-time `INVESTIGATION_REPORT` WebSocket broadcast appended to `broadcast_ingestion` pipeline.
- New `GET /api/investigations` and `POST /api/investigations/events/{event_id}/investigate` API endpoints.
- New unit and API integration tests covering investigation idempotency and mocking.

## [0.5.0] - 2026-09-22

### Added
- Phase 5: Multi-Signal Correlation and Contextual Risk Engine.
- Deterministic correlation engine evaluating context like temporal proximity and entity grouping.
- Risk Scorer yielding 0-100 bounded output.
- Severity classification mapping scores to explicit levels (LOW, MODERATE, HIGH, CRITICAL).
- Deterministic trace-based explanation generator.
- `RiskAssessment` persisted in SQLite.
- `GET /api/events/{event_id}/risk` endpoint.
- `RISK_ASSESSMENT` WebSocket payload generated automatically upon ingestion.
- Comprehensive scenario and unit testing for risk engine.

## [0.4.0] - 2026-09-21

### Added
- Phase 3.11: Baseline versioning with deterministic SHA-256 canonical hashing (`CanonicalBaseline.generate_version()`)
- Phase 3.12: Cold-start handling preventing false deviations via `BaselineStatus` (`NO_BASELINE`, `INSUFFICIENT_HISTORY`, `READY`)
- Phase 3.13: Baseline manual update policy and DB metadata (`UserBaseline.version`, `UserBaseline.status`)
- Phase 3.14: API integration (`GET /api/users/{user_id}/baseline`, `POST /api/users/{user_id}/baseline/rebuild`, `POST /api/events/{event_id}/behavioral-comparison`)
- Phase 3.15: Real-time WebSocket integration (`BEHAVIORAL_COMPARISON` broadcast upon event ingestion)
- Phase 3.16: Test suite expanded to 36/36 passing tests covering API and unit tests for cold-start and versioning logic.

## [0.3.0] — 2026-09-21

### Added
- Phase 3.5: Extended `NetworkBehaviorModel` with CIDR subnets (/24, /64) and IP version tracking
- Phase 3.6: Implemented `AuthenticationBehaviorModel` for outcome distributions, failure rates, and attempt counts
- Phase 3.7: Implemented `AccessPatternModel` for routing mechanisms (DIRECT, VPN, TOR)
- Phase 3.8: Implemented `BehavioralFeatureExtractor` for standardized per-event feature extraction
- Phase 3.9: Implemented `BaselineComparisonEngine` for objective delta calculations across 6 behavioral dimensions
- Phase 3.10: Implemented `DeviationEvidenceBuilder` for explainable, structured factual evidence generation
- Added `auth_profile` and `access_patterns` to `UserBaseline` and API responses
- Added comprehensive unit test suite in `tests/unit/test_baseline_expansion.py` (34/34 tests passing)

## [0.2.0] — 2026-09-21

### Added
- Phase 2: Canonical Ingestion Pipeline (`IngestionService`, `NormalizationService`, `EnrichmentService`)
- Phase 2: Synthetic Historical Dataset Generator (`SyntheticDataGenerator`, `ScenarioRunner`)
- Phase 3.1-3.5: Baseline Profile Engine and core models (Temporal, Device, Location, Network)

## [0.1.0] — 2026-09-21

### Added
- Project identity migration from ShadowGuard to ALIAS
- Project memory system (PROJECT_STATE.md, CHANGELOG.md, ARCHITECTURE.md)
- Complete documentation structure under docs/
- Phase tracking documentation (Phases 1–10)
- Feature documentation stubs
- Clean backend architecture under backend/app/
- Pydantic v2 configuration system
- SQLite database foundation
- SQLAlchemy models: LoginEvent, UserBaseline, AnomalyRecord, InvestigationReport
- Pydantic v2 API schemas
- FastAPI API routing foundation
- WebSocket alert infrastructure
- Service layer interfaces (EventService, BaselineService, InvestigationService)
- Detection module interfaces (AnomalyEngine, CorrelationEngine, RiskEngine)
- Investigation module interface
- Centralized error handling
- Structured logging
- Health check endpoints
- Login event ingestion endpoint
- Frontend foundation structure
- Testing foundation
- Updated README
- .env.example configuration template

### Changed
- Migrated project identity from ShadowGuard to ALIAS
- Fixed Pydantic v1/v2 configuration mismatch
- Replaced hardcoded IP addresses with localhost/environment configuration
- Replaced external Supabase dependency with local SQLite
- Fixed UTF-16 encoded database.py file
- Consolidated fragmented backend entry points

### Removed
- Hardcoded 192.168.137.1 references
- Supabase cloud database dependency for local development
- Presidio NLP dependency (not needed for login analysis)
- Mock deepfake video/audio analysis endpoints
