"""Phase 2 Integration Tests."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import uuid

def test_batch_ingestion(client: TestClient):
    """Test batch ingestion with success and duplicates."""
    batch_payload = {
        "events": [
            {
                "user_id": "sarah.connors@acme.corp",
                "ip_address": "1.1.1.1",
                "auth_status": "SUCCESS",
                "source_event_id": "unique_1"
            },
            {
                "user_id": "alex.mercer@acme.corp",
                "ip_address": "2.2.2.2",
                "auth_status": "FAILURE",
                "source_event_id": "unique_2"
            },
            {
                "user_id": "sarah.connors@acme.corp",
                "ip_address": "1.1.1.1",
                "auth_status": "SUCCESS",
                "source_event_id": "unique_1"  # Duplicate
            }
        ]
    }
    
    response = client.post("/api/events/batch", json=batch_payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["accepted"] == 2
    assert data["duplicates"] == 1
    assert data["total"] == 3
    
def test_history_and_baseline_pipeline(client: TestClient):
    """Test generation of synthetic data and baseline preparation."""
    # Generate history
    response = client.post("/api/system/generate/history?days=2")
    assert response.status_code == 200
    assert response.json()["accepted"] > 0
    
    # Generate baseline
    response = client.post("/api/system/generate/baselines")
    assert response.status_code == 200
    
    # Get user baseline
    response = client.get("/api/users/sarah.connors@acme.corp/baseline")
    assert response.status_code == 200
    baseline = response.json()
    assert baseline["login_count"] > 0
    assert len(baseline["known_ips"]) > 0

def test_scenario_playback(client: TestClient):
    """Test scenario playback feature."""
    response = client.post("/api/system/scenarios/impossible_travel")
    assert response.status_code == 200
    data = response.json()
    assert data["events_generated"] == 2
    assert data["events_ingested"] == 2
