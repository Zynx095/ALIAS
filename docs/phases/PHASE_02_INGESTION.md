# Phase 2: Ingestion Pipeline & Baseline Data

## Phase Metadata
- **Phase ID:** 2
- **Phase Name:** Ingestion Pipeline & Baseline Data
- **Status:** COMPLETE
- **Started:** 2026-09-21
- **Completed:** 2026-09-21
- **Prerequisites:** Phase 1 (Foundation Rebuild)

---

## 1. Objective & Intended Responsibility
The primary objective of Phase 2 is to design and implement a scalable authentication event ingestion pipeline and generate a realistic, synthetic historical dataset representing normal enterprise user behavior.

### Scope of Responsibility:
1. **Event Ingestion Handlers:** Extend `/api/v1/events/ingest` to support both single-event streaming and bulk batch uploads with schema validation and rate limiting.
2. **Telemetry Normalization:** Implement extractors for parsing raw IP addresses, extracting User-Agent details (OS, Browser, Device Class), and mapping IP addresses to geographic coordinates (City, Country, Latitude, Longitude).
3. **Synthetic Baseline Dataset Generation:** Build a deterministic simulation script generating 30 days of legitimate authentication activity for 50 enterprise users across various roles (e.g., standard employee, remote engineer, travelling executive).
4. **Database Seeding:** Provide automated seeding utilities to load baseline historical telemetry into the SQLite database for subsequent behavioral modeling.

---

## 2. Key Deliverables
- Batch and streaming ingestion endpoints with complete input validation.
- User-Agent and GeoIP enrichment utilities.
- Synthetic dataset generation utility (`scripts/generate_baseline_data.py`).
- Automated database seed runner (`scripts/seed_db.py`).
