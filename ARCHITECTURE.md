# ALIAS — System Architecture

## 1. System Overview

**ALIAS** (**AI-assisted Login Anomaly Investigation System**) is an enterprise-grade security investigation platform designed to ingest authentication telemetry. Target pipeline: Login Events → Feature Extraction → Behavioral Baseline → Anomaly Detection → Multi-Signal Correlation → Risk Scoring → AI Investigation → Explainable Findings
- Backend structure (FastAPI, SQLAlchemy, Pydantic v2, SQLite)
- Frontend structure (React, Vite, Tailwind)
- Database schema overview (`LoginEvent`, `UserBaseline`, `AnomalyRecord`, `RiskAssessment`, `InvestigationReport`).

Transitioned from the legacy ShadowGuard identity, ALIAS specifically focuses on simulated and live enterprise authentication events (IAM/IdP/SSO/VPN), replacing brittle rule heuristics and unverified mock deepfake models with a disciplined, end-to-end security operations pipeline.

---

## 2. Target Pipeline Flow

The core ALIAS data and detection pipeline processes events through eight distinct stages:

```
+---------------------------------------------------------------------------------------------------+
|                                      ALIAS PROCESSING PIPELINE                                     |
+---------------------------------------------------------------------------------------------------+

 [1. Login Events]       --> Simulated or live authentication telemetry (IP, Device, Geo, MFA, Result)
         |
         v
 [2. Feature Extraction] --> Parses timestamps, device fingerprints, ASN/ISP, geolocation, user identity
         |
         v
 [3. Behavioral Baseline]--> Historical profile comparison (typical hours, known devices, regular locations)
         |
         v
 [4. Anomaly Detection]  --> Multi-signal detector evaluation (Geo velocity, device shift, off-hours, brute force)
         |
         v
 [5. Multi-Signal Corr.] --> Time-window correlation grouping anomalies across identity, IP, and session
         |
         v
 [6. Risk Scoring]       --> Composite risk scoring engine (0-100 score, Low/Medium/High/Critical severity)
         |
         v
 [7. AI Investigation]   --> LLM-assisted forensic analyst: prompt assembly, contextual synthesis, hypothesis testing
         |
         v
 [8. Explainable Report] --> Human-readable investigation report, MITRE ATT&CK mapping, recommended remediations
```

---

## 3. Technology Stack

| Component | Technology | Version / Specification | Rationale |
|-----------|------------|-------------------------|-----------|
| **Backend Framework** | FastAPI | >= 0.110.0 | High-performance asynchronous Python REST & WebSocket framework |
| **Data Validation** | Pydantic v2 / pydantic-settings | >= 2.0 | High-speed schema validation, strict settings management |
| **ORM & Persistence** | SQLAlchemy + SQLite | SQLAlchemy >= 2.0 | Async-capable ORM, file-backed local zero-friction database |
| **Authentication & Security** | Passlib (bcrypt) + python-jose | JWT (HS256) | Standard role-based access control and token handling |
| **Real-Time Layer** | FastAPI WebSockets | Starlette WebSocket | Instant push of correlated alert bursts to SOC frontends |
| **Frontend Framework** | React 19 + Vite | Vite 6 | Modern, lightning-fast component rendering and HMR |
| **Styling & Design** | Tailwind CSS 4 | Tailwind v4 | Dynamic utility styling without legacy CSS bloat |
| **Visualization** | Recharts + Framer Motion | Latest | Security charts, velocity diagrams, risk gauges, globe projection |
| **AI Investigation** | Structured LLM Interface | OpenAI / Local LLM (Phase 6) | Automated narrative generation and triage recommendations |

---

## 4. Backend Architecture

The backend follows clean architecture principles with strict separation of concerns across configuration, persistence, validation schemas, business services, detection interfaces, and API routers.

### 4.1 Layer Responsibilities

```
backend/app/
├── api/          # HTTP & WebSocket route handlers (thin controllers)
├── core/         # Global configuration (Pydantic Settings), logging, exceptions
├── models/       # SQLAlchemy ORM database models
├── schemas/      # Pydantic v2 request/response validation schemas
├── services/     # Core domain business logic (EventService, BaselineService, etc.)
├── detection/    # Anomaly detection, signal correlation, risk scoring interfaces
├── security/     # JWT authentication, password hashing, RBAC dependencies
├── websocket/    # ConnectionManager for active SOC client broadcast
└── workers/      # Asynchronous worker jobs and ingestion helpers
```

### 4.2 Network & Binding Configuration
- **Localhost Only**: The system strictly binds to `127.0.0.1` / `localhost` by default.
- **Dynamic Configuration**: All networking endpoints, CORS origins, and port bindings are governed by environment variables via `backend/app/core/config.py` (`Settings` class). Hardcoded LAN IPs (such as `192.168.137.1`) are forbidden.

---

## 5. Database Schema & Data Models

ALIAS utilizes SQLite via SQLAlchemy for reliable local development and testing, maintaining strict relations and indices for rapid query response.

```
+---------------------------------------------------------------------------------+
|                               DATABASE ENTITY RELATIONSHIPS                      |
+---------------------------------------------------------------------------------+

     +-----------------------+              +-----------------------+
     |      LoginEvent       |              |     UserBaseline      |
     +-----------------------+              +-----------------------+
     | id: String(PK)        |              | id: String(PK)        |
     | timestamp: DateTime   |              | user_id: String (UQ)  |
     | user_id: String (IDX) |<--+          | typical_hours: JSON   |
     | ip_address: String    |   |          | known_devices: JSON   |
     | city: String          |   |          | known_locations: JSON |
     | country: String       |   |          | avg_login_freq: Float |
     | device_type: String   |   |          | last_updated: DateTime|
     | user_agent: String    |   |          +-----------------------+
     | status: Enum(S/F)     |   |
     | failure_reason: String|   |
     | session_id: String    |   |
     +-----------------------+   |
                 |               |
                 v               |
     +-----------------------+   |
     |     AnomalyRecord     |   |
     +-----------------------+   |
     | id: String(PK)        |   |
     | event_id: FK(Login)   |---+
     | user_id: String (IDX) |
     | anomaly_type: String  |
     | severity: Enum        |
     | score: Float (0-100)  |
     | details: JSON         |
     | detected_at: DateTime |
     +-----------------------+
                 |
                 v
     +-----------------------+
     |  InvestigationReport  |
     +-----------------------+
     | id: String(PK)        |
     | title: String         |
     | target_user: String   |
     | risk_score: Float     |
     | summary: Text         |
     | mitre_tactics: JSON   |
     | recommended_action:Str|
     | status: Enum          |
     | generated_at: DateTime|
     +-----------------------+
```

### Key Models:
1. **`LoginEvent`**: Records raw telemetry of simulated or real authentication attempts, including geo coordinates, network identifiers, browser/OS fingerprint, and outcome.
2. **`UserBaseline`**: Aggregated behavioral norm per user (customary active hours, known IP subnets, frequent geographic hubs, average login cadence).
3. **`AnomalyRecord`**: Specific anomaly signal flagged by detection engines (e.g., impossible travel, unknown device, atypical time, credential stuffing burst).
4. **`InvestigationReport`**: Synthesized forensic dossier containing multi-signal correlations, MITRE ATT&CK mappings, AI narrative summary, and mitigation steps.

---

## 6. Service Layer Pattern & Detection Interfaces

Business logic is decoupled from HTTP transport. Routes delegate directly to service classes:

- **`EventService`**: Handles ingestion, validation, normalization, and persistence of raw login events.
- **`BaselineService`**: Computes, retrieves, and updates behavioral profile summaries from event histories.
- **`InvestigationService`**: Coordinates multi-signal queries, initiates investigation workflows, and persists reports.

### Detection Engines (Modular Interfaces)
- **`AnomalyEngine`**: Abstract contract for modular anomaly checks:
  - `DeviceAnomalyDetector`: Identifies novel User-Agent / device signatures.
  - `GeoVelocityDetector`: Calculates physical speed between successive logins (impossible travel).
  - `TemporalAnomalyDetector`: Evaluates deviations from normal active hours.
  - `BruteForceDetector`: Tracks failure spikes and IP-based credential attacks.
- **`CorrelationEngine`**: Aggregates anomalies across configurable sliding time windows.
- **`RiskEngine`**: Weighs anomaly scores and frequency to produce a composite risk rating (0-100).

*(Note: In Phase 1, detection and investigation engines provide stable type-hinted abstract interfaces with stubbed passes; algorithmic logic is implemented in Phases 3–6).*

---

## 7. Real-Time WebSocket Architecture

The backend provides a non-blocking WebSocket gateway (`/ws/alerts`) managed by `ConnectionManager`:
1. SOC Analyst clients establish a persistent WebSocket connection upon dashboard initialization.
2. When the ingestion or correlation pipeline classifies an event as high or critical severity, an event payload is published to the `ConnectionManager`.
3. Active connections receive broadcast JSON frames within sub-second latency, triggering live dashboard visual updates, alert sound cues, and map pings without client polling.

---

## 8. Frontend Architecture

The frontend is a single-page application built on Vite, React 19, and Tailwind CSS 4.

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── src/
    ├── api/           # Axios/Fetch client with automatic token attachment
    ├── assets/        # Static imagery, icons, and logo assets
    ├── components/    # Reusable UI widgets (Charts, Maps, Tables, Badges, Modals)
    ├── context/       # AuthContext, WebSocketContext, AlertContext
    ├── hooks/         # Custom React hooks (useWebSocket, useAuth, useEvents)
    ├── layouts/       # MainLayout with SOC navigation sidebar and top header
    ├── pages/         # Primary views (Dashboard, Events, Investigations, Settings)
    ├── styles/        # Tailwind root styles and design tokens
    └── utils/         # Time formatting, geo math, risk color mapping
```

---

## 9. Project Directory Tree

```
alias/
├── .env.example                      # Environment variables blueprint
├── ARCHITECTURE.md                  # System architecture specification (this file)
├── CHANGELOG.md                     # Version and change history
├── IMPLEMENTATION_PLAN.md           # 10-Phase roadmap and delivery milestones
├── PROJECT_STATE.md                 # Live phase tracking and project health
├── README.md                        # Project introduction and quickstart
├── REQUIREMENTS.md                  # Detailed dependency and environment requirements
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── anomalies.py
│   │   │   ├── events.py
│   │   │   ├── health.py
│   │   │   ├── investigations.py
│   │   │   ├── risk.py
│   │   │   ├── router.py
│   │   │   ├── system.py
│   │   │   └── users.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Pydantic v2 Settings class
│   │   │   ├── errors.py            # Custom exceptions and exception handlers
│   │   │   └── logging.py           # Structured JSON / console logger
│   │   ├── detection/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # Abstract detector contracts
│   │   │   ├── correlation.py       # Signal correlation interfaces
│   │   │   └── risk.py              # Risk scoring interfaces
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── anomaly.py           # AnomalyRecord SQLAlchemy model
│   │   │   ├── baseline.py          # UserBaseline SQLAlchemy model
│   │   │   ├── database.py          # Engine, sessionmaker, Base
│   │   │   ├── event.py             # LoginEvent SQLAlchemy model
│   │   │   └── investigation.py     # InvestigationReport SQLAlchemy model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── anomaly.py           # Anomaly Pydantic schemas
│   │   │   ├── baseline.py          # Baseline Pydantic schemas
│   │   │   ├── event.py             # LoginEvent Pydantic schemas
│   │   │   └── investigation.py     # Investigation Pydantic schemas
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Password hashing & JWT creation/verification
│   │   │   └── rbac.py              # Role permissions & scopes
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── baseline_service.py  # Baseline calculation logic
│   │   │   ├── event_service.py     # Ingestion & search business logic
│   │   │   └── investigation_service.py # Report orchestration logic
│   │   ├── websocket/
│   │   │   ├── __init__.py
│   │   │   └── manager.py           # WebSocket ConnectionManager
│   │   └── main.py                  # FastAPI application entrypoint
│   └── tests/                       # Backend test suite
├── docs/
│   ├── api/                         # OpenAPI specs and endpoint notes
│   ├── architecture/                # Architecture diagrams and specifications
│   ├── decisions/                   # Architecture Decision Records (ADRs)
│   ├── features/                    # Feature specifications
│   ├── phases/                      # Detailed phase delivery runbooks
│   └── testing/                     # Test plans and coverage reports
└── frontend/
    ├── public/                      # Static assets
    ├── src/                         # React 19 source tree
    ├── package.json                 # Frontend dependencies
    └── vite.config.js               # Vite bundler configuration
```
