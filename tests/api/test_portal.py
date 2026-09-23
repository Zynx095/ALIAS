"""Tests for Protected Application Portal authentication and telemetry delivery."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from fastapi.testclient import TestClient
from main import app
from models.database import SessionLocal, LoginEvent


@pytest.fixture
def client():
    return TestClient(app)


def test_portal_config(client):
    """Test retrieving portal presets configuration."""
    response = client.get("/api/portal/config")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "locations" in data
    assert "devices" in data
    assert any(u["key"] == "yukith" for u in data["users"])
    assert any(loc["key"] == "tokyo" for loc in data["locations"])


def test_portal_brute_force_sequence_and_no_credential_leakage(client):
    """
    Test consecutive failed login attempts followed by successful login,
    verifying failed_attempts incrementation and ensuring zero credential leakage into ALIAS events.
    """
    client.post("/api/portal/reset-counters")

    # 1. Attempt 1: Failed login
    res1 = client.post("/api/portal/login", json={
        "username": "yukith",
        "password": "wrong_password_1",
        "location_preset": "new_york"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["success"] is False
    assert data1["auth_status"] == "FAILURE"
    assert data1["failed_attempts"] == 1
    assert data1["telemetry_delivered"] is True
    event_id_1 = data1["event_id"]

    # 2. Attempt 2: Failed login
    res2 = client.post("/api/portal/login", json={
        "username": "yukith",
        "password": "wrong_password_2",
        "location_preset": "new_york"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["success"] is False
    assert data2["auth_status"] == "FAILURE"
    assert data2["failed_attempts"] == 2

    # 3. Attempt 3: Failed login with Tokyo location changer
    res3 = client.post("/api/portal/login", json={
        "username": "yukith",
        "password": "wrong_password_3",
        "location_preset": "tokyo"
    })
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["success"] is False
    assert data3["failed_attempts"] == 3
    assert data3["location"] == "Tokyo, JP"
    assert data3["ip_address"] == "203.0.113.88"

    # 4. Attempt 4: Successful login with correct password
    res4 = client.post("/api/portal/login", json={
        "username": "yukith",
        "password": "YukithSecure2026!",
        "location_preset": "new_york"
    })
    assert res4.status_code == 200
    data4 = res4.json()
    assert data4["success"] is True
    assert data4["auth_status"] == "SUCCESS"
    assert data4["failed_attempts"] == 3  # Reports preceding failures
    event_id_4 = data4["event_id"]

    # 5. Security audit: Inspect the actual database row to prove passwords never enter ALIAS
    db = SessionLocal()
    try:
        event = db.query(LoginEvent).filter(LoginEvent.id == event_id_1).first()
        assert event is not None
        assert event.user_id == "yukith"
        assert event.auth_status == "FAILURE"
        # Ensure model has no password column or leak
        assert not hasattr(event, "password")
        assert not hasattr(event, "password_hash")
    finally:
        db.close()
