"""API tests for AI Investigations."""
from fastapi.testclient import TestClient

def test_list_investigations_empty(client: TestClient):
    response = client.get("/api/investigations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_trigger_and_get_investigation(client: TestClient):
    # 1. Ingest an event to get an ID
    event_data = {
        "user_id": "api_investigation_user",
        "ip_address": "4.4.4.4",
        "user_agent": "Mozilla/5.0",
        "auth_status": "SUCCESS"
    }
    ingest_resp = client.post("/api/events/login", json=event_data)
    assert ingest_resp.status_code in (200, 201)
    event_id = ingest_resp.json()["event_id"]
    
    # 2. Trigger investigation manually
    trig_resp = client.post(f"/api/investigations/events/{event_id}/investigate", json={"force_reevaluate": True})
    assert trig_resp.status_code == 200
    report = trig_resp.json()
    assert report["event_id"] == event_id
    assert report["user_id"] == "api_investigation_user"
    assert "mock-fallback" in report["llm_provider"]
    
    # 3. Get investigation by event
    get_resp = client.get(f"/api/investigations/events/{event_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["investigation_id"] == report["investigation_id"]
