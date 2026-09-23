"""Tests for login event endpoints."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from fastapi.testclient import TestClient
from main import app

# DB dependency override and schema lifecycle are owned by the session-scoped
# fixtures in conftest.py, which point the shared `app` at test_alias.db.
# This file previously set its own app.dependency_overrides[get_db] to a
# separate test_events.db at import time; since that override is never
# restored, it silently hijacked every other test file's DB access for the
# rest of the pytest session.


@pytest.fixture
def client():
    return TestClient(app)


def test_post_login_event(client):
    """Test creating a login event via POST."""
    payload = {
        'user_id': 'sarah.connors@acme.corp',
        'ip_address': '203.0.113.42',
        'latitude': 12.9716,
        'longitude': 77.5946,
        'location': 'Bengaluru, India',
        'device_fingerprint': 'win11-chrome-abc123',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0)',
        'auth_status': 'SUCCESS',
        'failed_attempts': 0
    }
    response = client.post('/api/events/login', json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data['status'] == 'accepted'
    assert data['user_id'] == 'sarah.connors@acme.corp'
    assert 'event_id' in data
    assert data['processing_status'] == 'INGESTED'


def test_post_login_event_minimal(client):
    """Test creating a login event with minimum fields."""
    payload = {
        'user_id': 'minimal.user',
        'ip_address': '10.0.0.1'
    }
    response = client.post('/api/events/login', json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data['status'] == 'accepted'


def test_post_login_event_invalid_ip(client):
    """Test that invalid IP address is rejected."""
    payload = {
        'user_id': 'test.user',
        'ip_address': 'not-an-ip'
    }
    response = client.post('/api/events/login', json=payload)
    assert response.status_code == 422


def test_post_login_event_missing_user(client):
    """Test that missing user_id is rejected."""
    payload = {
        'ip_address': '10.0.0.1'
    }
    response = client.post('/api/events/login', json=payload)
    assert response.status_code == 422


def test_get_events_list(client):
    """Test listing events after creation."""
    response = client.get('/api/events')
    assert response.status_code == 200
    data = response.json()
    assert 'items' in data
    assert 'total' in data
    assert data['total'] >= 0


def test_get_single_event(client):
    """Test retrieving a specific event."""
    # First create an event
    payload = {
        'user_id': 'retrieval.test',
        'ip_address': '192.168.1.1'
    }
    create_resp = client.post('/api/events/login', json=payload)
    event_id = create_resp.json()['event_id']

    # Then retrieve it
    response = client.get(f'/api/events/{event_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == event_id
    assert data['user_id'] == 'retrieval.test'


def test_get_nonexistent_event(client):
    """Test that requesting a nonexistent event returns 404."""
    response = client.get('/api/events/99999')
    assert response.status_code == 404


def test_websocket_connect(client):
    """Test that WebSocket endpoint accepts connections."""
    with client.websocket_connect('/ws/alerts') as websocket:
        # Connection successful — just verify we can connect
        pass
