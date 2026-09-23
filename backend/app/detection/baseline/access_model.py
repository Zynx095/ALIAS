"""ALIAS Access Pattern Model.

Extracts historical access and routing modes (DIRECT, VPN, PROXY, etc.)
from login events without assigning risk or threat classifications.
"""
from typing import List
from models.database import LoginEvent
from schemas.baseline import AccessPatternProfile


class AccessPatternModel:
    """Models historical network access and routing patterns."""

    @staticmethod
    def build_profile(events: List[LoginEvent]) -> AccessPatternProfile:
        """Constructs an AccessPatternProfile from historical events."""
        if not events:
            return AccessPatternProfile()

        pattern_usage = {}
        last_seen_pattern = None

        sorted_events = sorted(events, key=lambda e: e.timestamp)

        for event in sorted_events:
            pattern = (event.access_pattern or "DIRECT").upper()
            pattern_usage[pattern] = pattern_usage.get(pattern, 0) + 1
            last_seen_pattern = pattern

        total_patterns = sum(pattern_usage.values())
        primary_patterns = []
        if total_patterns > 0:
            threshold = total_patterns * 0.20
            for pattern, count in pattern_usage.items():
                if count >= threshold:
                    primary_patterns.append(pattern)

        return AccessPatternProfile(
            known_access_patterns=list(pattern_usage.keys()),
            access_pattern_counts=pattern_usage,
            primary_access_patterns=primary_patterns,
            last_seen_access_pattern=last_seen_pattern
        )
