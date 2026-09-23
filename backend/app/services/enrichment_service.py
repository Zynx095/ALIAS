"""ALIAS Enrichment Service.

Enriches normalized events with metadata (time-of-day, IP type)
without making security judgments.
"""
from typing import Dict, Any

class EnrichmentService:
    """Service to enrich canonical events."""

    @staticmethod
    def enrich(canonical_event: dict) -> dict:
        """
        Enrich a normalized event in-place.
        Adds an 'enriched_data' dictionary to the event.
        """
        enriched = {}
        
        # IP Version
        ip = canonical_event.get("ip_address", "")
        if ":" in ip:
            enriched["ip_version"] = "IPv6"
        elif "." in ip:
            enriched["ip_version"] = "IPv4"
            
        # Temporal Enrichment
        ts = canonical_event.get("timestamp")
        if ts:
            enriched["hour_of_day"] = ts.hour
            enriched["day_of_week"] = ts.weekday()
            enriched["is_weekend"] = ts.weekday() >= 5
            
        # Optional: Basic User Agent parsing could go here, but for now
        # we just add the structure.
        
        canonical_event["enriched_data"] = enriched
        return canonical_event
