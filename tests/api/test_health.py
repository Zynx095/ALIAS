"""Tests for health check endpoints."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from conftest import client as client_fixture
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint returns ALIAS info."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'ALIAS'
    assert 'version' in data
    assert data['status'] == 'operational'


def test_health_endpoint(client):
    """Test the root health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['app'] == 'ALIAS'


def test_api_health_endpoint(client):
    """Test the API health endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['app_name'] == 'ALIAS'
    assert 'timestamp' in data
