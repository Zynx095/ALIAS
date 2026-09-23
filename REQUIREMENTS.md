# ALIAS — System & Software Requirements

## 1. System Requirements

### Host Environment
- **Operating System:** Windows 10/11, macOS 12+, or Linux (Ubuntu 22.04 LTS / Debian 12 recommended)
- **Processor:** 64-bit multi-core CPU (x86_64 or ARM64)
- **Memory (RAM):** Minimum 4 GB (8 GB recommended for running backend + frontend concurrently)
- **Disk Storage:** Minimum 2 GB free disk space

### Runtime Environments
- **Python:** Version `>= 3.10` (Python 3.10, 3.11, or 3.12 supported)
- **Node.js:** Version `>= 18.0.0` (LTS 20.x recommended)
- **Package Managers:**
  - Python: `pip` (version >= 23.0)
  - Node.js: `npm` (version >= 9.0)

---

## 2. Backend Dependencies (Python)

### Core Framework & Networking
- **`fastapi`** (`>= 0.110.0`): Asynchronous web API framework and WebSocket server.
- **`uvicorn[standard]`** (`>= 0.28.0`): High-performance ASGI production server.
- **`python-dotenv`** (`>= 1.0.0`): Environment variable loader for local `.env` configuration.

### Data Modeling & Persistence
- **`pydantic`** (`>= 2.6.0`): Data validation and parsing using Python type hints.
- **`pydantic-settings`** (`>= 2.2.0`): Configuration management using environment variables.
- **`sqlalchemy`** (`>= 2.0.28`): Database toolkit and Object-Relational Mapper (ORM).
- **`sqlite3`**: Built-in Python library for local database operations.

### Security & Authentication
- **`python-jose[cryptography]`** (`>= 3.3.0`): JSON Web Token (JWT) encoding, signing, and verification.
- **`passlib[bcrypt]`** (`>= 1.7.4`): Password hashing using bcrypt.
- **`python-multipart`** (`>= 0.0.9`): Form data parsing support for OAuth2 authentication flows.

### Testing & Quality Assurance
- **`pytest`** (`>= 8.0.0`): Unit and functional test framework.
- **`pytest-asyncio`** (`>= 0.23.5`): Async test runner for asynchronous FastAPI handlers.
- **`httpx`** (`>= 0.27.0`): Next-generation HTTP client for async API integration tests.

### Note on Future Machine Learning & AI Dependencies
> [!NOTE]
> Machine learning libraries such as `scikit-learn`, `numpy`, `pandas`, or LLM client libraries (`openai`, `anthropic`, `langchain`) are **intentionally excluded** from Phase 1. They are scheduled for introduction in **Phase 4** (Statistical Anomaly Detection) and **Phase 6** (AI Investigation). Phase 1 maintains a clean, zero-bloat foundation.

---

## 3. Frontend Dependencies (JavaScript / React)

### Core Build & Framework
- **`react`** (`^18.0.0` or `^19.0.0`): User interface component library.
- **`react-dom`** (`^18.0.0` or `^19.0.0`): DOM rendering engine for React.
- **`vite`** (`^6.0.0`): Modern frontend build tool and hot-module replacement dev server.

### Styling & Design System
- **`tailwindcss`** (`^4.0.0`): Utility-first CSS styling framework.
- **`lucide-react`** (`^0.400.0`): High-clarity iconography for SOC interface elements.
- **`framer-motion`** (`^11.0.0`): Declarative animation and real-time alert toast transitions.

### Data Visualization & Geolocation
- **`recharts`** (`^2.12.0`): Responsive charting library for anomaly trends and baseline deviations.
- **`react-globe.gl`** (`^2.27.0`): 3D geospatial globe component for visualizing impossible travel and international login telemetry.

---

## 4. Environment & Network Configuration

- **Default API Host:** `127.0.0.1` (Localhost)
- **Default Backend Port:** `8000`
- **Default Frontend Port:** `5173`
- **CORS Allowed Origins:** `["http://localhost:5173", "http://127.0.0.1:5173"]`
- **Hardcoded LAN IPs:** Strictly prohibited (no static `192.168.137.1` addresses permitted).
