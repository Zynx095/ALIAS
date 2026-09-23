"""Tests for Pydantic schemas."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from schemas.login import LoginEventRequest, LoginEventResponse
from schemas.common import HealthResponse
from datetime import datetime
from pydantic import ValidationError


class TestLoginEventRequest:
    """Tests for LoginEventRequest schema validation."""

    def test_valid_login_event(self):
        """Test that a valid login event passes validation."""
        event = LoginEventRequest(
            user_id='sarah.connors@acme.corp',
            ip_address='203.0.113.42',
            latitude=12.9716,
            longitude=77.5946,
            location='Bengaluru, India',
            device_fingerprint='win11-chrome-abc123',
            auth_status='SUCCESS',
            failed_attempts=0
        )
        assert event.user_id == 'sarah.connors@acme.corp'
        assert event.ip_address == '203.0.113.42'
        assert event.auth_status == 'SUCCESS'

    def test_minimal_login_event(self):
        """Test minimum required fields."""
        event = LoginEventRequest(
            user_id='user1',
            ip_address='10.0.0.1'
        )
        assert event.user_id == 'user1'
        assert event.auth_status == 'SUCCESS'  # default
        assert event.failed_attempts == 0  # default

    def test_missing_user_id_fails(self):
        """Test that missing user_id raises validation error."""
        with pytest.raises(ValidationError):
            LoginEventRequest(ip_address='10.0.0.1')

    def test_missing_ip_address_fails(self):
        """Test that missing ip_address raises validation error."""
        with pytest.raises(ValidationError):
            LoginEventRequest(user_id='user1')

    def test_invalid_ip_address_fails(self):
        """Test that an invalid IP address raises validation error."""
        with pytest.raises(ValidationError):
            LoginEventRequest(user_id='user1', ip_address='not-an-ip')

    def test_invalid_auth_status_fails(self):
        """Test that invalid auth_status raises validation error."""
        with pytest.raises(ValidationError):
            LoginEventRequest(user_id='user1', ip_address='10.0.0.1', auth_status='MAYBE')

    def test_latitude_out_of_range_fails(self):
        """Test latitude bounds."""
        with pytest.raises(ValidationError):
            LoginEventRequest(user_id='user1', ip_address='10.0.0.1', latitude=91.0)

    def test_longitude_out_of_range_fails(self):
        """Test longitude bounds."""
        with pytest.raises(ValidationError):
            LoginEventRequest(user_id='user1', ip_address='10.0.0.1', longitude=181.0)

    def test_negative_failed_attempts_fails(self):
        """Test that negative failed_attempts raises validation error."""
        with pytest.raises(ValidationError):
            LoginEventRequest(user_id='user1', ip_address='10.0.0.1', failed_attempts=-1)

    def test_ipv6_address_valid(self):
        """Test that IPv6 addresses are accepted."""
        event = LoginEventRequest(
            user_id='user1',
            ip_address='2001:db8::1'
        )
        assert event.ip_address == '2001:db8::1'

    def test_auth_status_normalized_to_uppercase(self):
        """Test that auth_status is normalized to uppercase."""
        event = LoginEventRequest(
            user_id='user1',
            ip_address='10.0.0.1',
            auth_status='success'
        )
        assert event.auth_status == 'SUCCESS'


class TestHealthResponse:
    """Tests for HealthResponse schema."""

    def test_health_response(self):
        health = HealthResponse(
            status='healthy',
            app_name='ALIAS',
            version='0.1.0',
            environment='testing',
            database='connected',
            timestamp=datetime.utcnow()
        )
        assert health.status == 'healthy'
        assert health.app_name == 'ALIAS'
