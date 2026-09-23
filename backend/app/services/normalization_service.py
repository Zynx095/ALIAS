"""ALIAS Normalization Service.

Normalizes valid raw events into a canonical internal format.
"""
from datetime import datetime, timezone
from schemas.ingestion import RawLoginEvent

class NormalizationService:
    """Service to normalize incoming events into a canonical format."""

    @staticmethod
    def normalize(event: RawLoginEvent) -> dict:
        """
        Normalize a validated event.
        - Timestamps forced to UTC.
        - Strings stripped and case-normalized.
        - Location parsed consistently.
        """
        # Ensure timestamp is UTC
        canonical_timestamp = event.timestamp
        if canonical_timestamp:
            if canonical_timestamp.tzinfo is None:
                # Assume UTC if no timezone is provided (as per system convention)
                canonical_timestamp = canonical_timestamp.replace(tzinfo=timezone.utc)
            else:
                canonical_timestamp = canonical_timestamp.astimezone(timezone.utc)
        else:
            canonical_timestamp = datetime.now(timezone.utc)
            
        # Strip string fields
        location = event.location.strip() if event.location else None
        device = event.device_fingerprint.strip() if event.device_fingerprint else None
        agent = event.user_agent.strip() if event.user_agent else None
        
        # Access pattern canonicalization
        access_pattern = event.access_pattern.upper().strip() if event.access_pattern else "DIRECT"

        return {
            "user_id": event.user_id.lower().strip(),  # Normalize identity to lowercase
            "ip_address": event.ip_address.strip(),
            "latitude": event.latitude,
            "longitude": event.longitude,
            "location": location,
            "device_fingerprint": device,
            "user_agent": agent,
            "timestamp": canonical_timestamp.replace(tzinfo=None), # Store as naive UTC datetime for SQLAlchemy
            "auth_status": event.auth_status.upper().strip(),
            "failed_attempts": event.failed_attempts,
            "access_pattern": access_pattern,
            "source_event_id": event.source_event_id.strip() if event.source_event_id else None,
            "source": event.source.upper().strip()
        }
