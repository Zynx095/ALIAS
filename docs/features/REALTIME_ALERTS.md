# Feature: WebSocket-Based Real-Time Alerting

## Metadata
- **Feature Name:** WebSocket-Based Real-Time Alerting
- **Status:** NOT IMPLEMENTED
- **Related Phase:** Phase 7 (API & WebSocket Integration)
- **Dependencies:** WebSocket ConnectionManager, FastAPI WebSocket endpoint

---

## 1. Description
Delivers sub-second alert notifications from the backend detection and correlation engines directly to connected SOC dashboard clients without client-side polling.

---

## 2. Intended Behavior
- **Persistent Bi-directional Gateway:** Exposes `/ws/alerts` for authenticated browser and client connections.
- **Connection Lifecycle Management:** Handles client registration, graceful disconnects, and channel subscription management.
- **Broadcast on High/Critical Thresholds:** Whenever the risk scoring engine classifies an event or correlated incident as High or Critical, the payload is serialized and broadcast to all active subscribers.
- **Resilience & Reconnect:** Implements client-side exponential backoff reconnection logic with heartbeat ping/pong messages to detect dropped connections.

---

## 3. Dependencies
- `backend/app/websocket/manager.py`
- `backend/app/main.py` (`/ws/alerts` route)
- Frontend WebSocket hook (`frontend/src/hooks/useWebSocket.js`)
