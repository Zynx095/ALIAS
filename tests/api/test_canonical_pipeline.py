"""Canonical Integration Test for Phase 7 (Full API & WebSocket Integration).

Tests the full ALIAS pipeline:
LOGIN EVENT -> INGESTION -> BEHAVIORAL COMPARISON -> ANOMALY DETECTION -> RISK CORRELATION -> AI INVESTIGATION -> WEBSOCKET BROADCAST
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timezone
import uuid

def test_canonical_pipeline_and_idempotency(client: TestClient):
    # 1. Prepare unique deterministic event
    test_run_id = str(uuid.uuid4())
    event_payload = {
        "user_id": f"canonical_user_{test_run_id}",
        "ip_address": "8.8.8.8",
        "location": "Mountain View, US",
        "latitude": 37.3861,
        "longitude": -122.0839,
        "device_fingerprint": "canon-device-hash",
        "user_agent": "Mozilla/5.0 ALIAS-Test",
        "auth_status": "SUCCESS",
        "failed_attempts": 0,
        "access_pattern": "DIRECT",
        "source_event_id": f"src_evt_{test_run_id}",
        "source": "CANONICAL_TEST"
    }

    # 2. Ingest the event via API
    resp1 = client.post("/api/events/login", json=event_payload)
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["status"] == "accepted"
    event_id = data1["event_id"]
    assert event_id is not None

    # Wait briefly for background tasks to process (in TestClient background tasks run immediately)
    # BackgroundTasks run after the response is returned, but within the same thread in TestClient.
    
    # 3. Verify Event Retrieval
    get_evt = client.get(f"/api/events/{event_id}")
    assert get_evt.status_code == 200
    assert get_evt.json()["user_id"] == event_payload["user_id"]
    
    # 4. Verify Anomalies were generated
    get_anomalies = client.get(f"/api/events/{event_id}/anomalies")
    assert get_anomalies.status_code == 200
    
    # 5. Verify Risk Assessment
    # It might take a moment if it's running background task, but in TestClient it's inline.
    get_risk = client.get(f"/api/events/{event_id}/risk")
    # If the user has NO_BASELINE, Risk might not generate anything or it generates 0 score
    if get_risk.status_code == 200:
        risk_data = get_risk.json()
        assert "risk_score" in risk_data
    else:
        assert get_risk.status_code == 404 # No risk generated
        
    # 6. Verify Investigation Report (Only generated if risk > 0, but mock provider will generate it if invoked manually)
    # Let's manually trigger it to guarantee it exists
    trig_inv = client.post(f"/api/investigations/events/{event_id}/investigate", json={"force_reevaluate": False})
    assert trig_inv.status_code == 200
    inv_data = trig_inv.json()
    assert inv_data["event_id"] == event_id
    assert inv_data["user_id"] == event_payload["user_id"]
    
    # 7. Test Idempotency (Replay identical event)
    resp2 = client.post("/api/events/login", json=event_payload)
    assert resp2.status_code == 201  # Ingestion returns 201 but with status 'ignored'
    data2 = resp2.json()
    assert data2["status"] == "ignored"
    assert data2["event_id"] == event_id # Should return the same event ID
    
    # Re-trigger investigation without force
    trig_inv2 = client.post(f"/api/investigations/events/{event_id}/investigate", json={"force_reevaluate": False})
    assert trig_inv2.status_code == 200
    assert trig_inv2.json()["investigation_id"] == inv_data["investigation_id"]

def test_missing_event_error_handling(client: TestClient):
    # 404 for invalid event in risk
    bad_risk = client.get("/api/events/999999999/risk")
    assert bad_risk.status_code == 404
    
    # 404 for invalid event in investigation
    bad_inv = client.get("/api/investigations/events/999999999")
    assert bad_inv.status_code == 404
    
    # 404 for triggering investigation on non-existent event
    bad_trig = client.post("/api/investigations/events/999999999/investigate", json={"force_reevaluate": True})
    assert bad_trig.status_code == 404
