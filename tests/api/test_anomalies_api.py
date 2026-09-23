import pytest
from fastapi.testclient import TestClient
from main import app
from models.database import get_db, Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Schema lifecycle is owned by the session-scoped fixture in conftest.py.
    # This file previously called Base.metadata.drop_all(bind=engine) here,
    # which drops the shared test_alias.db schema for the rest of the pytest
    # session (engine resolves to the same DB as conftest's test_engine).
    yield

def test_anomaly_scenario_new_device(setup_db):
    # 1. Ingest 5 events to establish baseline
    for i in range(5):
        resp = client.post("/api/events/login", json={
            "user_id": "test_anomaly_user",
            "ip_address": f"192.168.1.{i}",
            "device_fingerprint": "known_device",
            "auth_status": "SUCCESS",
            "source": "TEST"
        })
        assert resp.status_code == 201
        
    client.post("/api/users/test_anomaly_user/baseline/rebuild")

    # 2. Fire new event with a completely unseen device
    resp = client.post("/api/events/login", json={
        "user_id": "test_anomaly_user",
        "ip_address": f"192.168.1.5",
        "device_fingerprint": "NEW_EVIL_DEVICE",
        "auth_status": "SUCCESS",
        "source": "TEST"
    })
    
    assert resp.status_code == 201
    event_id = resp.json()["event_id"]
    
    # 3. Retrieve anomalies
    anom_resp = client.get(f"/api/events/{event_id}/anomalies")
    assert anom_resp.status_code == 200
    data = anom_resp.json()
    
    assert data["has_anomalies"] is True
    anomalies = data["anomalies"]
    
    # We expect a DEVICE anomaly
    device_anomalies = [a for a in anomalies if a["anomaly_type"] == "DEVICE_ANOMALY"]
    assert len(device_anomalies) > 0
    assert device_anomalies[0]["observed_value"] == "NEW_EVIL_DEVICE"
    assert "risk_score" not in device_anomalies[0]
