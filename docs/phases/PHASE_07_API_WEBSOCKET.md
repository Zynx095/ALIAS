# ALIAS Phase 7: API & WebSocket Integration

## 1. Overview
This document specifies the exact JSON payloads the ALIAS SOC Dashboard (Frontend) will receive via REST API and WebSockets. The backend pipeline enforces deterministic generation and execution order for all events, ensuring chronological delivery of the risk lifecycle.

## 2. API Endpoints Contract

All endpoints are mounted under `/api`.

### 2.1 Events
**POST** `/api/events/login`
- **Request:** `RawLoginEvent` schema (requires `user_id`, `ip_address`). Supports optional `source_event_id` for idempotency.
- **Response (201 Created):** 
```json
{
  "event_id": 1234,
  "user_id": "user_name",
  "status": "accepted",
  "timestamp": "2026-09-22T10:00:00Z"
}
```
*Note:* If a duplicate `source_event_id` or duplicate deterministic hash is provided, `status` will be `"ignored"`, preventing pipeline duplication.

**GET** `/api/events/{event_id}`
Returns the full enriched `LoginEventDetail`.

### 2.2 Anomalies
**GET** `/api/events/{event_id}/anomalies`
Returns the `AnomalyDetectionResponse`:
```json
{
  "event_id": 1234,
  "user_id": "user_name",
  "baseline_version": "sha256-hash",
  "has_anomalies": true,
  "detected_at": "2026-09-22T10:00:01Z",
  "anomalies": [
    {
      "anomaly_id": "uuid",
      "anomaly_type": "IMPOSSIBLE_TRAVEL",
      "detector": "LocationDetector",
      "signal": "LOCATION",
      "feature": "velocity",
      "observed_value": 1500,
      "expected_state": "< 1000",
      "explanation": "Impossible travel speed detected.",
      "rule_id": "LOC_001"
    }
  ]
}
```

### 2.3 Risk
**GET** `/api/events/{event_id}/risk`
Returns the `RiskAssessmentResponse`:
```json
{
  "risk_id": "uuid",
  "event_id": 1234,
  "user_id": "user_name",
  "risk_score": 75.0,
  "severity": "HIGH",
  "scoring_version": "risk_v1",
  "explanation": "Multiple correlated location and device anomalies.",
  "risk_factors": [...],
  "correlation_factors": [...],
  "correlated_anomalies": [...]
}
```

### 2.4 Investigation
**GET** `/api/investigations/events/{event_id}`
Returns the `InvestigationReportResponse`:
```json
{
  "investigation_id": "uuid",
  "event_id": 1234,
  "user_id": "user_name",
  "investigation_status": "COMPLETED",
  "llm_provider": "openai-gpt-4o",
  "summary": "The user engaged in impossible travel.",
  "verdict": "MALICIOUS",
  "confidence": "HIGH",
  "recommendations": ["Force password reset", "Block IP"]
}
```

## 3. WebSocket Real-Time Events Contract

**Endpoint:** `ws://<host>:<port>/ws/alerts`

All payloads are wrapped in the standard WebSocket envelope:
```json
{
  "type": "<EVENT_TYPE>",
  "event_id": "1234",
  "timestamp": "2026-09-22T10:00:00Z",
  "payload": { ... }
}
```

### 3.1 Chronological Emission Sequence
1. **`LOGIN_EVENT`**
   - Payload: `LoginEventResponse`
2. **`BEHAVIORAL_COMPARISON`**
   - Payload: `{"user_id": "...", "baseline_version": "...", "deviations": [...]}`
3. **`ANOMALY_DETECTED`** (Only if anomalies > 0)
   - Payload: `AnomalyDetectionResponse`
4. **`RISK_ASSESSMENT`**
   - Payload: `RiskAssessmentResponse`
5. **`INVESTIGATION_REPORT`** (Only if risk_score > 0)
   - Payload: `InvestigationReportResponse`

## 4. Idempotency and Reliability
- **Connection handling**: Inactive or broken WebSockets are safely reaped. Reconnection is supported.
- **Deduplication**: Replaying identical raw events uses a SHA-256 event hash (or `source_event_id`). The ingestor immediately returns `"ignored"` and **does not** enqueue the event for background pipeline evaluation or WebSocket broadcast.
- **Atomic Operations**: Broadcasts execute strictly *after* successful database commits to prevent emitting alerts for data that failed to persist.
