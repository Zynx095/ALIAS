"""Login event API schemas."""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re

class LoginEventRequest(BaseModel):
    """Schema for incoming login event submission."""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")
    ip_address: str = Field(..., description="Client IP address (IPv4 or IPv6)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Geographic latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Geographic longitude")
    location: Optional[str] = Field(None, max_length=255, description="Human-readable location (City, Country)")
    device_fingerprint: Optional[str] = Field(None, max_length=255, description="Device fingerprint hash")
    user_agent: Optional[str] = Field(None, description="Browser/client user agent string")
    timestamp: Optional[datetime] = Field(None, description="Login timestamp (defaults to server time)")
    auth_status: str = Field("SUCCESS", description="Authentication result: SUCCESS or FAILURE")
    failed_attempts: int = Field(0, ge=0, description="Number of preceding failed login attempts")
    access_pattern: Optional[str] = Field(None, description="Access pattern: DIRECT, VPN, TOR, PROXY")

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        # Basic IP validation (IPv4 or IPv6)
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        ipv6_pattern = r'^[0-9a-fA-F:]+$'
        if not (re.match(ipv4_pattern, v) or re.match(ipv6_pattern, v)):
            raise ValueError("Invalid IP address format")
        return v

    @field_validator("auth_status")
    @classmethod
    def validate_auth_status(cls, v: str) -> str:
        allowed = {"SUCCESS", "FAILURE"}
        if v.upper() not in allowed:
            raise ValueError(f"auth_status must be one of: {allowed}")
        return v.upper()

    model_config = {"json_schema_extra": {"examples": [{"user_id": "sarah.connors@acme.corp", "ip_address": "203.0.113.42", "latitude": 12.9716, "longitude": 77.5946, "location": "Bengaluru, India", "device_fingerprint": "win11-chrome-abc123", "user_agent": "Mozilla/5.0 (Windows NT 10.0)", "auth_status": "SUCCESS", "failed_attempts": 0}]}}


class LoginEventResponse(BaseModel):
    """Response after a login event is ingested."""
    status: str = "accepted"
    event_id: int
    user_id: str
    processing_status: str = "INGESTED"
    timestamp: datetime
    message: str = "Login event ingested successfully"

    model_config = {"from_attributes": True}


class LoginEventDetail(BaseModel):
    """Full login event details."""
    id: int
    user_id: str
    ip_address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[str] = None
    device_fingerprint: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    auth_status: str
    failed_attempts: int
    access_pattern: Optional[str] = None
    processing_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
