"""ALIAS Ingestion Schemas.

Defines schemas for the ingestion pipeline, ensuring raw input validation
and internal event consistency before processing.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re

class RawLoginEvent(BaseModel):
    """Schema for incoming login event payload, either single or batch."""
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
    source_event_id: Optional[str] = Field(None, max_length=64, description="Unique ID from source system for idempotency")
    source: str = Field("API", max_length=50, description="Source of the event (API, BATCH, SCENARIO)")

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        v = v.strip()
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

class BatchLoginEventRequest(BaseModel):
    """Schema for batch login event ingestion."""
    events: List[RawLoginEvent] = Field(..., max_length=1000, description="List of raw login events")

class BatchIngestionResult(BaseModel):
    """Result of batch ingestion."""
    accepted: int
    duplicates: int
    rejected: int
    total: int
    event_ids: List[int]
    errors: List[dict] = []
