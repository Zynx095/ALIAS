"""ALIAS Scenario Runner.

Executes predefined scenarios by generating events and pushing them through
the canonical ingestion pipeline.
"""
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from schemas.ingestion import RawLoginEvent

class ScenarioRunner:
    """Generates ingestible events based on scenarios."""

    @staticmethod
    def get_scenario(scenario_id: str, user_id: str = "sarah.connors@acme.corp") -> List[RawLoginEvent]:
        """
        Returns a sequence of raw events for a scenario.
        """
        events = []
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        
        if scenario_id == "impossible_travel":
            # Event 1: Normal login in Bengaluru
            events.append(RawLoginEvent(
                user_id=user_id,
                ip_address="203.0.113.45",
                latitude=12.9716,
                longitude=77.5946,
                location="Bengaluru, India",
                device_fingerprint="primary_device_hash",
                timestamp=now,
                auth_status="SUCCESS",
                source="SCENARIO_RUNNER",
                source_event_id=str(uuid.uuid4())
            ))
            
            # Event 2: Login from Frankfurt 10 minutes later
            events.append(RawLoginEvent(
                user_id=user_id,
                ip_address="198.51.100.14",
                latitude=50.1109,
                longitude=8.6821,
                location="Frankfurt, Germany",
                device_fingerprint="secondary_device_hash",
                timestamp=now,
                auth_status="SUCCESS",
                source="SCENARIO_RUNNER",
                source_event_id=str(uuid.uuid4())
            ))
            
        elif scenario_id == "brute_force":
            # 5 failed logins, then 1 success
            ip = "192.0.2.200"
            for i in range(5):
                events.append(RawLoginEvent(
                    user_id=user_id,
                    ip_address=ip,
                    device_fingerprint="unknown_attacker_device",
                    timestamp=now,
                    auth_status="FAILURE",
                    failed_attempts=i+1,
                    source="SCENARIO_RUNNER",
                    source_event_id=str(uuid.uuid4())
                ))
            
            events.append(RawLoginEvent(
                user_id=user_id,
                ip_address=ip,
                device_fingerprint="unknown_attacker_device",
                timestamp=now,
                auth_status="SUCCESS",
                failed_attempts=5,
                source="SCENARIO_RUNNER",
                source_event_id=str(uuid.uuid4())
            ))
            
        else:
            raise ValueError(f"Unknown scenario_id: {scenario_id}")
            
        return events
