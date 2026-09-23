# ALIAS

**AI-assisted Login Anomaly Investigation System**

ALIAS is a cybersecurity investigation platform that analyzes authentication events to detect suspicious login behavior using multi-signal anomaly detection and AI-assisted forensic investigation.

---

## What ALIAS Does

ALIAS monitors login/authentication events and identifies unusual behavior by analyzing:

- **IP address & geolocation** — Detecting impossible travel and geographic anomalies
- **Device fingerprinting** — Identifying new or unauthorized devices
- **Login timestamps** — Finding off-hours or unusual timing patterns
- **Failed login attempts** — Detecting brute-force or credential stuffing attacks
- **Access patterns** — Identifying VPN, TOR, or proxy usage anomalies

When suspicious activity is detected, ALIAS correlates multiple signals, calculates a risk score, and uses AI to generate human-readable investigation reports with recommended security actions.

---

## Current Status

**Phase 1 — Foundation** ✅

The project foundation is established with:
- Clean FastAPI backend with modular architecture
- SQLite database with login event, baseline, anomaly, and investigation models
- Pydantic v2 API schemas with validation
- RESTful API endpoints for event ingestion and retrieval
- WebSocket infrastructure for real-time alerts
- React + Vite frontend with SOC dashboard foundation
- Structured logging and error handling
- Testing foundation

**Not yet implemented:**
- Anomaly detection algorithms (Phase 4)
- Behavioral baseline engine (Phase 3)
- Multi-signal correlation (Phase 5)
- AI investigation with LLM (Phase 6)
- Full SOC dashboard redesign (Phase 8)
- Demo scenarios (Phase 9)

---

## Architecture

```
Login Events → Data Ingestion → Feature Extraction → Behavioral Baseline
    → Anomaly Detection → Multi-Signal Correlation → Risk Scoring
    → AI Investigation → Explainable Findings → SOC Dashboard
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic v2 |
| Database | SQLite (local dev) |
| Frontend | React, Vite, Tailwind CSS 4, Recharts |
| Real-time | WebSocket |
| AI Layer | LLM integration (future) |
| Desktop | Tauri v2 (optional) |

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Backend Setup

```bash
# From project root
cd backend/app

# Install Python dependencies
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv passlib

# Start the backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

### Quick Start (Windows)

```bash
# Double-click or run:
start_alias.bat
```

---

## Environment Configuration

Copy `.env.example` to `.env` and customize:

```env
DATABASE_URL=sqlite:///./alias.db
JWT_SECRET=change-me-in-production
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
```

---

## API Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | `/` | Root info | ✅ Active |
| GET | `/health` | Quick health check | ✅ Active |
| GET | `/api/health` | Detailed health check | ✅ Active |
| POST | `/api/events/login` | Ingest a login event | ✅ Active |
| GET | `/api/events` | List login events | ✅ Active |
| GET | `/api/events/{id}` | Get specific event | ✅ Active |
| GET | `/api/events/{id}/investigation` | Get investigation report | 🔧 Foundation |
| WS | `/ws/alerts` | Real-time alerts | ✅ Active |
| GET | `/docs` | Swagger API documentation | ✅ Active |

---

## Testing

```bash
# From project root
python -m pytest tests/ -v
```

---

## Project Phases

| Phase | Name | Status |
|-------|------|--------|
| 0 | Audit & Architecture | ✅ Complete |
| 1 | Foundation Rebuild | ✅ Complete |
| 2 | Ingestion Pipeline & Baseline Data | ⬜ Not Started |
| 3 | Behavioral Baseline Engine | ⬜ Not Started |
| 4 | Anomaly Detection | ⬜ Not Started |
| 5 | Correlation & Risk Scoring | ⬜ Not Started |
| 6 | AI Investigation | ⬜ Not Started |
| 7 | API & WebSocket Integration | ⬜ Not Started |
| 8 | SOC Dashboard | ⬜ Not Started |
| 9 | Demo Scenarios | ⬜ Not Started |
| 10 | Testing & Verification | ⬜ Not Started |

---

## License

Private — Educational/Hackathon Project
