import pytest
from fastapi.testclient import TestClient
from main import app
from models.database import get_db, Base, engine, UserBaseline, LoginEvent

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Schema lifecycle is owned by the session-scoped fixture in conftest.py.
    # This file previously called Base.metadata.drop_all(bind=engine) here,
    # which drops the shared test_alias.db schema for the rest of the pytest
    # session (engine resolves to the same DB as conftest's test_engine).
    yield

def test_api_rebuild_and_comparison(setup_db):
    # 1. Ingest 5 events to reach READY threshold
    for i in range(5):
        resp = client.post("/api/events/login", json={
            "user_id": "test_user_api",
            "ip_address": f"192.168.1.{i}",
            "device_fingerprint": "device_x",
            "auth_status": "SUCCESS",
            "source": "TEST"
        })
        assert resp.status_code == 201

    # 2. Rebuild Baseline
    rebuild_resp = client.post("/api/users/test_user_api/baseline/rebuild")
    assert rebuild_resp.status_code == 200
    data = rebuild_resp.json()
    assert data["status"] == "READY"
    assert data["login_count"] == 5
    assert data["version"].startswith("bsl_")

    # 3. Get Baseline
    get_resp = client.get("/api/users/test_user_api/baseline")
    assert get_resp.status_code == 200
    b_data = get_resp.json()
    assert b_data["status"] == "READY"
    assert b_data["version"] == data["version"]

    # 4. Ingest an event and test comparison directly
    resp_ev = client.post("/api/events/login", json={
        "user_id": "test_user_api",
        "ip_address": "10.10.10.10", # New IP
        "device_fingerprint": "device_y", # New Device
        "auth_status": "SUCCESS",
        "source": "TEST"
    })
    event_id = resp_ev.json()["event_id"]

    comp_resp = client.post(f"/api/events/{event_id}/behavioral-comparison")
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    
    assert comp_data["baseline_version"] == data["version"]
    assert comp_data["comparison_status"] == "READY"
    assert comp_data["has_deviations"] is True
    assert "DEVICE" in comp_data["deviating_dimensions"]
    assert "NETWORK" in comp_data["deviating_dimensions"]
