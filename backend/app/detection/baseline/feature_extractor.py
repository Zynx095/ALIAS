"""ALIAS Behavioral Feature Extraction.

Phase 3.8: Extracts normalized, structured behavioral features from a single
login event (model, schema, or dict) for subsequent baseline comparison.
"""
from typing import Union, Dict, Any
from datetime import datetime

from models.database import LoginEvent
from schemas.baseline import EventBehavioralFeatures
from detection.baseline.network_model import NetworkBehaviorModel


class BehavioralFeatureExtractor:
    """Extracts structured behavioral features from incoming authentication events."""

    @classmethod
    def extract_features(cls, event: Union[LoginEvent, Dict[str, Any], Any]) -> EventBehavioralFeatures:
        """
        Extracts standardized EventBehavioralFeatures from a LoginEvent model,
        Pydantic model, or raw dictionary.
        """
        if isinstance(event, dict):
            user_id = event.get("user_id", "")
            ts = event.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            elif not isinstance(ts, datetime):
                ts = datetime.utcnow()

            ip_address = event.get("ip_address", "")
            device_fp = event.get("device_fingerprint")
            user_agent = event.get("user_agent")
            loc_name = event.get("location")
            lat = event.get("latitude")
            lon = event.get("longitude")
            auth_status = (event.get("auth_status") or "SUCCESS").upper()
            failed_attempts = int(event.get("failed_attempts") or 0)
            access_pattern = event.get("access_pattern")
            if access_pattern:
                access_pattern = access_pattern.upper()
        else:
            # SQLAlchemy model or Pydantic object
            user_id = getattr(event, "user_id", "")
            ts = getattr(event, "timestamp", None) or datetime.utcnow()
            ip_address = getattr(event, "ip_address", "")
            device_fp = getattr(event, "device_fingerprint", None)
            user_agent = getattr(event, "user_agent", None)
            loc_name = getattr(event, "location", None)
            lat = getattr(event, "latitude", None)
            lon = getattr(event, "longitude", None)
            auth_status = (getattr(event, "auth_status", "SUCCESS") or "SUCCESS").upper()
            failed_attempts = int(getattr(event, "failed_attempts", 0) or 0)
            access_pattern = getattr(event, "access_pattern", None)
            if access_pattern:
                access_pattern = access_pattern.upper()

        hour_of_day = ts.hour
        day_of_week = ts.weekday()
        is_weekend = day_of_week >= 5

        subnet = NetworkBehaviorModel._extract_subnet(ip_address) if ip_address else None
        ip_version = NetworkBehaviorModel._extract_ip_version(ip_address) if ip_address else "IPv4"

        return EventBehavioralFeatures(
            user_id=user_id,
            timestamp=ts,
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            device_fingerprint=device_fp,
            user_agent=user_agent,
            location_name=loc_name,
            latitude=lat,
            longitude=lon,
            ip_address=ip_address,
            subnet=subnet,
            ip_version=ip_version,
            auth_status=auth_status,
            failed_attempts=failed_attempts,
            access_pattern=access_pattern
        )
