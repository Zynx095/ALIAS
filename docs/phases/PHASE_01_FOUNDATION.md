# Phase 1: Foundation Rebuild

## Phase Metadata
- **Phase ID:** 1
- **Phase Name:** Foundation Rebuild
- **Status:** IN PROGRESS
- **Started:** 2026-09-21
- **Completed:** —
- **Prerequisites:** Phase 0 (Audit & Architecture)

---

## 1. Objective
Establish a clean, robust, and reproducible technical foundation for ALIAS. This phase resolves legacy architectural debt (purging hardcoded IP addresses, fixing UTF-16 encoding errors, removing broken Supabase/Presidio couplings, and upgrading to Pydantic v2) while building the core database models, validation schemas, service interfaces, detection engine contracts, logging, error handling, and API bootstrap.

> [!IMPORTANT]
> Phase 1 is **foundation only**. No machine learning algorithms, no mock deepfake analysis, and no synthetic detection shortcuts are implemented in this phase.

---

## 2. Comprehensive 20-Step Implementation Checklist

- [ ] **Step 1: Environment & Settings Configuration**
  Implement `backend/app/core/config.py` using `pydantic-settings` (Pydantic v2). Configure all networking, security secrets, CORS origins, and database connection strings through environment variables. Provide `.env.example`.

- [ ] **Step 2: Network Decoupling & Host Sanitization**
  Eliminate all hardcoded LAN IP addresses (specifically `192.168.137.1`). Ensure the default host binds strictly to `127.0.0.1` / `localhost`.

- [ ] **Step 3: Database Engine & Session Factory**
  Implement clean SQLite connection management in `backend/app/models/database.py` with standard UTF-8 encoding, foreign key enforcement, and a resilient `get_db` FastAPI dependency.

- [ ] **Step 4: SQLAlchemy Model — `LoginEvent`**
  Define `backend/app/models/event.py` for recording authentication events (timestamp, user_id, ip_address, city, country, latitude, longitude, device_type, user_agent, auth_status, failure_reason, session_id).

- [ ] **Step 5: SQLAlchemy Model — `UserBaseline`**
  Define `backend/app/models/baseline.py` for holding user profile baselines (typical login hours, habitual locations, known device fingerprints, average frequency).

- [ ] **Step 6: SQLAlchemy Model — `AnomalyRecord`**
  Define `backend/app/models/anomaly.py` for logging detected security anomalies (event_id, user_id, anomaly_type, severity, score, details).

- [ ] **Step 7: SQLAlchemy Model — `InvestigationReport`**
  Define `backend/app/models/investigation.py` for storing forensic investigation summaries (title, target_user, risk_score, summary, mitre_tactics, recommendations, status).

- [ ] **Step 8: Pydantic v2 Schemas — `LoginEvent`**
  Define `backend/app/schemas/event.py` with strict input validation for event ingestion and serialized output schemas.

- [ ] **Step 9: Pydantic v2 Schemas — `UserBaseline`**
  Define `backend/app/schemas/baseline.py` for representing baseline profiles and updates.

- [ ] **Step 10: Pydantic v2 Schemas — `AnomalyRecord`**
  Define `backend/app/schemas/anomaly.py` for anomaly payloads and alert broadcasts.

- [ ] **Step 11: Pydantic v2 Schemas — `InvestigationReport`**
  Define `backend/app/schemas/investigation.py` for investigative findings and remediation suggestions.

- [ ] **Step 12: Centralized Error Handling**
  Define `backend/app/core/errors.py` with domain-specific exceptions (`EntityNotFoundError`, `ValidationError`, `SecurityAnomalyError`) and global FastAPI exception handlers returning consistent JSON payloads.

- [ ] **Step 13: Structured Logging Infrastructure**
  Implement `backend/app/core/logging.py` providing standardized logging with contextual request IDs, timestamps, and severity levels.

- [ ] **Step 14: Service Layer Contract — `EventService`**
  Create `backend/app/services/event_service.py` to decouple database queries and event processing logic from HTTP route controllers.

- [ ] **Step 15: Service Layer Contract — `BaselineService`**
  Create `backend/app/services/baseline_service.py` defining interfaces for computing and querying behavioral profiles.

- [ ] **Step 16: Service Layer Contract — `InvestigationService`**
  Create `backend/app/services/investigation_service.py` defining interfaces for initiating investigations and assembling dossiers.

- [ ] **Step 17: Detection Engine Modular Interfaces**
  Create `backend/app/detection/base.py`, `correlation.py`, and `risk.py` declaring abstract base classes for anomaly detectors, correlation engines, and risk scoring calculators.

- [ ] **Step 18: WebSocket Connection Manager**
  Implement `backend/app/websocket/manager.py` with thread-safe client tracking, broadcast capabilities, and disconnect handling for the `/ws/alerts` gateway.

- [ ] **Step 19: API Endpoints Bootstrap**
  Implement health check endpoints (`/api/v1/health/live`, `/api/v1/health/ready`) and the initial login event ingestion endpoint (`/api/v1/events/ingest`).

- [ ] **Step 20: Application Assembly & Verification**
  Wire all routers and middleware into `backend/app/main.py`. Verify clean application startup with Uvicorn and run baseline smoke tests.

---

## 3. Deliverables
1. Functional FastAPI backend without deprecated dependencies.
2. Clean SQLite database initialized with all 4 core tables.
3. Unit test suite verifying model creation, schema parsing, and health endpoints.
4. Comprehensive project documentation suite.
