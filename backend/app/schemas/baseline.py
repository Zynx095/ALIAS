"""ALIAS Baseline Schemas.

Defines structured representations of behavioral profiles,
feature extraction formats, and deviation evidence.
Strictly descriptive: No security decisions, risk scores, or threat verdicts exist here.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class BaselineStatus(str, Enum):
    """Lifecycle state of a user's behavioral baseline."""
    NO_BASELINE = "NO_BASELINE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    READY = "READY"


class TemporalProfile(BaseModel):
    """Represents a user's historical time-based login behavior."""
    hourly_distribution: Dict[str, int] = Field(default_factory=dict, description="Counts of logins by hour of day (0-23)")
    workday_count: int = Field(0, description="Number of logins occurring Mon-Fri")
    weekend_count: int = Field(0, description="Number of logins occurring Sat-Sun")
    typical_hours: List[int] = Field(default_factory=list, description="List of hours (0-23) that represent typical activity (e.g. >5% frequency)")
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class DeviceProfile(BaseModel):
    """Represents a user's historical device usage."""
    known_devices: List[str] = Field(default_factory=list, description="Unique device fingerprints observed")
    device_usage_counts: Dict[str, int] = Field(default_factory=dict, description="Counts of logins per device fingerprint")
    primary_devices: List[str] = Field(default_factory=list, description="Devices making up the majority of logins")
    last_seen_device: Optional[str] = None


class LocationProfile(BaseModel):
    """Represents a user's historical geographic behavior."""
    known_locations: List[str] = Field(default_factory=list, description="Unique location strings (e.g., City, Country)")
    location_usage_counts: Dict[str, int] = Field(default_factory=dict, description="Counts of logins per location")
    primary_locations: List[str] = Field(default_factory=list, description="Most frequently visited locations")
    last_seen_location: Optional[str] = None
    last_seen_latitude: Optional[float] = None
    last_seen_longitude: Optional[float] = None


class NetworkProfile(BaseModel):
    """Represents a user's historical network behavior."""
    known_ips: List[str] = Field(default_factory=list, description="Unique IP addresses observed")
    ip_usage_counts: Dict[str, int] = Field(default_factory=dict, description="Counts of logins per IP address")
    primary_ips: List[str] = Field(default_factory=list, description="Most frequently used IP addresses")
    known_subnets: List[str] = Field(default_factory=list, description="CIDR subnets observed (e.g. /24 for IPv4, /64 for IPv6)")
    subnet_usage_counts: Dict[str, int] = Field(default_factory=dict, description="Counts of logins per subnet")
    primary_subnets: List[str] = Field(default_factory=list, description="Primary subnets observed")
    ip_versions_seen: List[str] = Field(default_factory=list, description="IP protocol versions observed (IPv4, IPv6)")
    last_seen_ip: Optional[str] = None


class AuthenticationProfile(BaseModel):
    """Represents a user's historical authentication outcome behavior."""
    total_attempts: int = Field(0, description="Total authentication attempts observed")
    successful_logins: int = Field(0, description="Successful logins observed")
    failed_logins: int = Field(0, description="Failed logins observed")
    failure_rate: float = Field(0.0, description="Ratio of failed logins to total attempts (0.0 - 1.0)")
    status_distribution: Dict[str, int] = Field(default_factory=dict, description="Count of logins by auth status (SUCCESS, FAILURE)")
    typical_failed_attempts_max: int = Field(0, description="Max failed attempts recorded before successful authentication")
    typical_failed_attempts_mean: float = Field(0.0, description="Average failed attempts count per event")
    last_auth_status: Optional[str] = None


class AccessPatternProfile(BaseModel):
    """Represents a user's historical access patterns (DIRECT, VPN, PROXY, etc.)."""
    known_access_patterns: List[str] = Field(default_factory=list, description="Unique access patterns observed")
    access_pattern_counts: Dict[str, int] = Field(default_factory=dict, description="Counts per access pattern")
    primary_access_patterns: List[str] = Field(default_factory=list, description="Most frequently observed access patterns (>20%)")
    last_seen_access_pattern: Optional[str] = None


class CanonicalBaseline(BaseModel):
    """The complete aggregated behavioral baseline for a user across 6 behavioral dimensions."""
    user_id: str
    total_logins: int
    temporal: TemporalProfile = Field(default_factory=TemporalProfile)
    device: DeviceProfile = Field(default_factory=DeviceProfile)
    location: LocationProfile = Field(default_factory=LocationProfile)
    network: NetworkProfile = Field(default_factory=NetworkProfile)
    authentication: AuthenticationProfile = Field(default_factory=AuthenticationProfile)
    access_pattern: AccessPatternProfile = Field(default_factory=AccessPatternProfile)
    status: BaselineStatus = Field(default=BaselineStatus.NO_BASELINE)
    baseline_version: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def generate_version(self) -> str:
        """Generates a deterministic SHA-256 version of the canonical baseline content."""
        import hashlib
        import json
        
        # Exclude random/metadata fields
        content = self.model_dump(
            exclude={"updated_at", "status", "baseline_version"},
            mode="json"
        )
        
        def sort_dict(item):
            if isinstance(item, dict):
                return {k: sort_dict(v) for k, v in sorted(item.items())}
            if isinstance(item, list):
                if item and all(isinstance(x, (str, int, float)) for x in item):
                    return sorted(item)
                return [sort_dict(x) for x in item]
            return item
            
        canonical_dict = sort_dict(content)
        canonical_str = json.dumps(canonical_dict, separators=(',', ':'))
        
        version_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        self.baseline_version = f"bsl_{version_hash[:16]}"
        return self.baseline_version


# ============================================================
# Phase 3.8: Behavioral Feature Extraction Schema
# ============================================================

class EventBehavioralFeatures(BaseModel):
    """Normalized, extracted behavioral features from a single login event."""
    user_id: str
    timestamp: datetime
    baseline_version: Optional[str] = None
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    is_weekend: bool
    device_fingerprint: Optional[str] = None
    user_agent: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ip_address: str
    subnet: Optional[str] = None
    ip_version: str = "IPv4"
    auth_status: str = "SUCCESS"
    failed_attempts: int = 0
    access_pattern: Optional[str] = None


# ============================================================
# Phase 3.9: Baseline Comparison Schemas
# ============================================================

class DimensionDeviation(BaseModel):
    """Objective deviation details for a single behavioral dimension."""
    dimension: str
    is_deviant: bool
    details: Dict[str, Any] = Field(default_factory=dict)


class BaselineComparisonResult(BaseModel):
    """Complete multi-dimensional comparison of an event against a baseline."""
    user_id: str
    timestamp: datetime
    baseline_version: Optional[str] = None
    comparison_status: BaselineStatus = Field(default=BaselineStatus.READY)
    deviations: Dict[str, DimensionDeviation] = Field(default_factory=dict)
    has_deviations: bool = False


# ============================================================
# Phase 3.10: Deviation Evidence Schemas
# ============================================================

class DeviationEvidence(BaseModel):
    """A structured, factual, human-readable evidence item for a specific deviation."""
    dimension: str  # TEMPORAL, DEVICE, LOCATION, NETWORK, AUTHENTICATION, ACCESS_PATTERN
    feature_name: str
    is_deviant: bool
    observed_value: Any
    baseline_expected: Any
    evidence_text: str


class DeviationEvidenceReport(BaseModel):
    """A structured report containing all explainable evidence items for a login event."""
    user_id: str
    timestamp: datetime
    baseline_version: Optional[str] = None
    comparison_status: BaselineStatus = Field(default=BaselineStatus.READY)
    evidence_items: List[DeviationEvidence] = Field(default_factory=list)
    deviating_dimensions: List[str] = Field(default_factory=list)
    has_deviations: bool = False
    summary: str = ""
