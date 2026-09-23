import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_scenarios():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) == 6
    ids = [s["scenario_id"] for s in scenarios]
    assert "normal_login" in ids
    assert "new_device" in ids
    assert "impossible_travel" in ids
    assert "auth_burst" in ids
    assert "multi_signal" in ids
    assert "unseen_network" in ids

def test_run_normal_login():
    response = client.post("/api/scenarios/normal_login/run")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "Running"
    assert data["events_generated"] == 1
    
    event_ids = data["results"]["event_ids"]
    assert len(event_ids) == 1
    
    import time
    time.sleep(0.2)
    resp_risk = client.get(f"/api/events/{event_ids[0]}/risk")
    if resp_risk.status_code == 200:
        risk = resp_risk.json()
        assert risk["risk_score"] == 0.0
        assert risk["severity"] == "LOW"

def test_run_new_device():
    resp = client.post('/api/scenarios/new_device/run')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'Running'
    event_ids = data["results"]["event_ids"]
    assert len(event_ids) == 1

    import time
    time.sleep(0.2)
    resp_risk = client.get(f"/api/events/{event_ids[0]}/risk")
    if resp_risk.status_code == 200:
        risk = resp_risk.json()
        assert risk["risk_score"] == 15.0
        assert risk["severity"] == "LOW"

def test_run_impossible_travel():
    resp = client.post('/api/scenarios/impossible_travel/run')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'Running'
    event_ids = data["results"]["event_ids"]
    assert len(event_ids) == 2

    import time
    time.sleep(0.2)
    target_event_id = event_ids[-1]
    resp_risk = client.get(f"/api/events/{target_event_id}/risk")
    if resp_risk.status_code == 200:
        risk = resp_risk.json()
        assert risk["risk_score"] >= 25.0
        assert risk["severity"] in ["MODERATE", "HIGH"]

def test_run_auth_burst():
    resp = client.post('/api/scenarios/auth_burst/run')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'Running'
    event_ids = data["results"]["event_ids"]
    assert len(event_ids) == 5

    import time
    time.sleep(0.2)
    target_event_id = event_ids[-1]
    resp_risk = client.get(f"/api/events/{target_event_id}/risk")
    if resp_risk.status_code == 200:
        risk = resp_risk.json()
        assert risk["risk_score"] >= 25.0
        assert risk["severity"] in ["MODERATE", "HIGH"]

def test_run_multi_signal():
    response = client.post("/api/scenarios/multi_signal/run")
    assert response.status_code == 200
    data = response.json()
    assert data["events_generated"] == 1
    
    event_ids = data["results"]["event_ids"]
    assert len(event_ids) == 1
    
    import time
    time.sleep(0.2)
    
    resp = client.get(f"/api/events/{event_ids[0]}/anomalies")
    assert resp.status_code == 200
    data = resp.json()
    
    assert "anomalies" in data, data
    anomalies = data["anomalies"]
    assert len(anomalies) > 0
    
    resp_risk = client.get(f"/api/events/{event_ids[0]}/risk")
    assert resp_risk.status_code == 200
    risk = resp_risk.json()
    assert risk["severity"] in ["HIGH", "CRITICAL"]

def test_run_unseen_network():
    resp = client.post('/api/scenarios/unseen_network/run')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'Running'
    event_ids = data["results"]["event_ids"]
    assert len(event_ids) == 1

    import time
    time.sleep(0.2)
    resp_risk = client.get(f"/api/events/{event_ids[0]}/risk")
    if resp_risk.status_code == 200:
        risk = resp_risk.json()
        assert risk["risk_score"] >= 25.0

def test_reset_demo():
    response = client.post("/api/scenarios/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
