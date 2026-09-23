# Feature: Login Event Ingestion & Storage

## Metadata
- **Feature Name:** Login Event Ingestion & Storage
- **Status:** FOUNDATION
- **Related Phase:** Phase 1 (Foundation Rebuild), Phase 2 (Ingestion Pipeline & Baseline Data)
- **Dependencies:** SQLite / SQLAlchemy, Pydantic v2 validation schemas

---

## 1. Description
Provides the telemetry entry point for ALIAS, allowing identity providers (IdPs), Single Sign-On (SSO) gateways, VPN servers, and simulation scripts to push authentication and login events into the system for real-time analysis and historical profiling.

---

## 2. Intended Behavior
- **Data Ingestion:** Accepts single or batched JSON payloads via REST endpoint `/api/v1/events/ingest`.
- **Validation & Parsing:** Validates all fields against the Pydantic v2 `LoginEventCreate` schema, verifying timestamps, IPv4/IPv6 format, coordinate ranges, and status enumerations (`SUCCESS`, `FAILURE`).
- **Telemetry Enrichment:** Enriches events with extracted device fingerprints (browser engine, operating system) and resolved geolocation (city, country, latitude, longitude).
- **Persistent Storage:** Commits validated records to the `login_events` table with indexation on `user_id`, `timestamp`, and `status`.
- **Pipeline Forwarding:** Dispatches persisted events to behavioral baseline and anomaly detection workers for inline inspection.

---

## 3. Dependencies
- `backend/app/models/event.py` (SQLAlchemy ORM model)
- `backend/app/schemas/event.py` (Pydantic v2 schemas)
- `backend/app/services/event_service.py` (Service business logic)
- `backend/app/api/endpoints/events.py` (API route controller)
