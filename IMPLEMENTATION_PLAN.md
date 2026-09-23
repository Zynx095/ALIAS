# ALIAS — 10-Phase Implementation Plan

## Executive Summary
This document provides the roadmap for building **ALIAS** (**AI-assisted Login Anomaly Investigation System**). The project is structured across 10 progressive phases, beginning with architectural auditing and foundation rebuilding, advancing through telemetry ingestion, behavioral baselining, multi-signal anomaly detection, correlation, AI forensic investigation, and culminating in real-time SOC dashboard visualization and rigorous verification.

---

## Roadmap Overview

| Phase | Phase Name | Status | Target Timeline | Pre-requisites |
|:-----:|------------|:------:|:---------------:|:---------------|
| **Phase 0** | Audit & Architecture | ✅ COMPLETE | Day 1 | None |
| **Phase 1** | Foundation Rebuild | 🔄 IN PROGRESS | Day 1–2 | Phase 0 |
| **Phase 2** | Ingestion Pipeline & Baseline Data | ⬜ NOT STARTED | Day 2–3 | Phase 1 |
| **Phase 3** | Behavioral Baseline Engine | ⬜ NOT STARTED | Day 3–4 | Phase 2 |
| **Phase 4** | Anomaly Detection | ⬜ NOT STARTED | Day 4–5 | Phase 3 |
| **Phase 5** | Multi-Signal Correlation & Risk Scoring | ✅ COMPLETE | Day 5-6 | Phase 4 |
| **Phase 6** | AI-Assisted Investigation | ✅ COMPLETE | Day 6-7 | Phase 5 |
| **Phase 7** | API & WebSocket Integration | ✅ COMPLETE | Day 7-8 | Phase 5, Phase 6 |
| **Phase 8** | SOC Dashboard | ✅ COMPLETE | Day 8–9 | Phase 7 |
| **Phase 9** | Demo Scenarios | ⬜ NOT STARTED | Day 9–10 | Phase 6, Phase 8 |
| **Phase 10** | Testing & Verification | ⬜ NOT STARTED | Day 10 | All Phases |

---

## Detailed Phase Breakdown

### Phase 0: Audit & Architecture
- **Status:** ✅ COMPLETE
- **Objective:** Audit the legacy codebase (ShadowGuard), purge broken dependencies and hardcoded network addresses, define the new ALIAS system boundaries, and establish the documentation architecture.
- **Key Deliverables:**
  - System audit report and migration plan.
  - Identification of legacy issues (Pydantic v1/v2 mismatches, UTF-16 encoded files, hardcoded LAN IP addresses).
  - High-level architecture specification.
- **Dependencies:** None.

---

### Phase 1: Foundation Rebuild
- **Status:** 🔄 IN PROGRESS
- **Objective:** Establish a rock-solid, production-grade foundation for backend and frontend components without premature ML algorithms or mock results.
- **Key Deliverables:**
  - Standardized `.env` and `core/config.py` using Pydantic v2 `BaseSettings`.
  - Clean SQLite database initialization with UTF-8 encoding.
  - Core SQLAlchemy ORM models (`LoginEvent`, `UserBaseline`, `AnomalyRecord`, `InvestigationReport`).
  - Typed Pydantic v2 schemas for all entities.
  - FastAPI application bootstrap with CORS, structured logging, and centralized error handling.
  - Service layer interfaces (`EventService`, `BaselineService`, `InvestigationService`).
  - Detection module abstract interfaces (`AnomalyEngine`, `CorrelationEngine`, `RiskEngine`).
  - Real-time WebSocket connection manager.
  - Health check endpoints (`/api/v1/health/live`, `/api/v1/health/ready`).
  - Baseline ingestion endpoint stub.
- **Dependencies:** Phase 0.

---

### Phase 2: Ingestion Pipeline & Baseline Data
- **Status:** ⬜ NOT STARTED
- **Objective:** Create realistic authentication event generators, parsers, and data ingestion pipelines capable of processing batch and streaming login telemetry.
- **Key Deliverables:**
  - Ingestion endpoint `/api/v1/events/ingest` with batch and single event support.
  - Normalization pipeline: GeoIP resolution, User-Agent device parsing, IP CIDR tagging.
  - Synthetic enterprise authentication dataset generator (normal historical baseline data for ~50 users over 30 days).
  - Database seeding utility for populating authentic baseline profiles.
- **Dependencies:** Phase 1.

---

### Phase 3: Behavioral Baseline Engine
- **Status:** ⬜ NOT STARTED
- **Objective:** Build the statistical profiling engine that computes and maintains dynamic user behavioral baselines.
- **Key Deliverables:**
  - Historical behavioral profile aggregator (login frequency, time-of-day distributions, habitual IP ranges, known devices).
  - Rolling baseline update worker triggered by verified legitimate logins.
  - Baseline inquiry API endpoints (`/api/v1/baselines/{user_id}`).
  - Persistence and caching for user behavioral fingerprints.
- **Dependencies:** Phase 2.

---

### Phase 4: Anomaly Detection
- **Status:** ⬜ NOT STARTED
- **Objective:** Implement deterministic and statistical anomaly detectors evaluating individual authentication events against historical profiles.
- **Key Deliverables:**
  - `DeviceAnomalyDetector`: Identifies new browser, OS, or hardware signature shifts.
  - `GeoVelocityDetector`: Calculates impossible travel speed between consecutive logins using Haversine distance.
  - `TemporalAnomalyDetector`: Flags logins occurring during atypical hours for that user.
  - `BruteForceDetector`: Detects rapid failure bursts and password spray patterns.
  - `IPReputationDetector`: Flags known tor exit nodes, proxies, and untrusted CIDRs.
  - Anomaly record persistence and scoring.
- **Dependencies:** Phase 3.

---

### Phase 5: Multi-Signal Correlation & Risk Scoring
- **Status:** ⬜ NOT STARTED
- **Objective:** Correlate disparate anomaly signals occurring across sessions or time windows, scoring cumulative threat risk.
- **Key Deliverables:**
  - Sliding time-window correlation engine grouping anomalies by user, IP, or organization.
  - Multi-signal correlation rules (e.g., failed logins + sudden geo-hop + new device = high severity).
  - Quantitative composite risk scoring algorithm (0 to 100).
  - Severity classification: Low (0-29), Medium (30-59), High (60-84), Critical (85-100).
  - Automated alert trigger mechanism for High/Critical incidents.
- **Dependencies:** Phase 4.

---

### Phase 6: AI-Assisted Investigation
- **Status:** ✅ COMPLETE
- **Objective:** Integrate an LLM-assisted forensic investigator to analyze correlated anomaly clusters and formulate structured investigative dossiers.
- **Key Deliverables:**
  - LLM prompt engineering orchestrator assembling telemetry, baseline divergence, and timeline facts.
  - Structured investigation report generator:
    - Incident summary narrative.
    - MITRE ATT&CK tactic & technique mapping (e.g., T1078, T1110).
    - Confidence score and evidence chain.
    - Prescribed remediation steps (e.g., revoke tokens, force MFA reset, block IP).
  - Fallback deterministic rule-based explainer when LLM provider is offline.
  - Investigation review and state management API (`/api/v1/investigations`).
- **Dependencies:** Phase 5.

---

### Phase 7: API & WebSocket Integration
- **Status:** ✅ COMPLETE
- **Objective:** Finalize the ALIAS API boundaries and real-time event distribution mechanism for seamless frontend integration.
- **Key Deliverables:**
  - Comprehensive REST API endpoints for all ALIAS entities.
  - WebSocket `/ws/alerts` streaming real-time alerts with JSON schemas.
  - JWT-based authentication and role-based access control (Analyst, Admin, Auditor).
  - OpenAPI / Swagger documentation and test collection.
- **Dependencies:** Phase 5, Phase 6.

---

### Phase 8: SOC Dashboard
- **Status:** ✅ COMPLETE
- **Objective:** Provide a real-time security analyst workspace to triage events based on AI insights.
- **Key Deliverables:**
  - Real-time Alert Feed with visual priority indicators and audio notifications.
  - Geospatial Login Map showing login locations and impossible travel vectors.
  - User Baseline Profiler view visualizing normal vs. anomalous behavior.
  - AI Investigation Dossier view with interactive evidence cards and MITRE tags.
  - Quick remediation action buttons (e.g., "Isolate User", "Acknowledge Alert").
- **Dependencies:** Phase 7.

---

### Phase 9: Demo Scenarios
- **Status:** ⬜ NOT STARTED
- **Objective:** Create automated, reproducible end-to-end attack simulation scenarios demonstrating ALIAS detection and AI investigation capabilities.
- **Key Deliverables:**
  - Scenario 1: **Impossible Travel Attack** (Login in New York followed 15 minutes later in Moscow).
  - Scenario 2: **Credential Stuffing / Password Spray** (100 failed logins across users from rotating IPs, followed by 1 success).
  - Scenario 3: **Off-Hours Privilege Abuse** (Executive account accessed at 3:00 AM from a novel mobile device).
  - Scenario runner script (`scripts/run_demo.py`) with guided terminal output and instant dashboard reflection.
- **Dependencies:** Phase 6, Phase 8.

---

### Phase 10: Testing & Verification
- **Status:** ⬜ NOT STARTED
- **Objective:** Conduct rigorous unit, integration, end-to-end, and performance testing across the entire platform.
- **Key Deliverables:**
  - Backend unit test suite (`pytest`) covering services, models, schemas, and detection logic.
  - Integration tests verifying event ingestion to report generation pipeline.
  - WebSocket load and reconnect resiliency testing.
  - Frontend component and end-to-end validation.
  - Final verification sign-off report.
- **Dependencies:** All previous phases.
