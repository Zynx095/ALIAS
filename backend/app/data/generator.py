"""ALIAS Synthetic Data Generator.

Deterministically generates synthetic historical login events for baseline modeling.
"""
import random
from datetime import datetime, timedelta, timezone
import hashlib
from typing import List
import uuid

from schemas.ingestion import RawLoginEvent

USERS = ["sarah.connors@acme.corp", "alex.mercer@acme.corp", "david.vance@acme.corp"]

class SyntheticDataGenerator:
    """Generates deterministic synthetic login data."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        
    def _generate_ip(self) -> str:
        return f"{self.rng.randint(1,255)}.{self.rng.randint(0,255)}.{self.rng.randint(0,255)}.{self.rng.randint(1,254)}"
        
    def _generate_device(self, user_id: str) -> str:
        # 80% primary device, 20% secondary
        if self.rng.random() < 0.8:
            return hashlib.md5(f"{user_id}_primary".encode()).hexdigest()
        else:
            return hashlib.md5(f"{user_id}_secondary".encode()).hexdigest()
            
    def _generate_location(self, user_id: str):
        locations = {
            "sarah.connors@acme.corp": {"loc": "Bengaluru, India", "lat": 12.9716, "lon": 77.5946},
            "alex.mercer@acme.corp": {"loc": "Frankfurt, Germany", "lat": 50.1109, "lon": 8.6821},
            "david.vance@acme.corp": {"loc": "San Francisco, USA", "lat": 37.7749, "lon": -122.4194},
        }
        return locations.get(user_id, {"loc": "Unknown", "lat": 0.0, "lon": 0.0})

    def generate_history(self, days: int = 30, events_per_user_per_day: int = 2) -> List[RawLoginEvent]:
        """Generate historical baseline login events."""
        events = []
        end_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        for user in USERS:
            # Deterministic per user based on general seed
            user_rng = random.Random(f"{self.seed}_{user}")
            loc = self._generate_location(user)
            user_ip = f"{user_rng.randint(1,255)}.{user_rng.randint(0,255)}.100.100"
            
            for day_offset in range(days):
                current_day = start_time + timedelta(days=day_offset)
                
                # Skip some weekends randomly
                if current_day.weekday() >= 5 and user_rng.random() < 0.7:
                    continue
                    
                for _ in range(events_per_user_per_day):
                    # Random time during workday (8 AM to 6 PM)
                    hour = user_rng.randint(8, 17)
                    minute = user_rng.randint(0, 59)
                    event_time = current_day.replace(hour=hour, minute=minute)
                    
                    auth_status = "SUCCESS" if user_rng.random() < 0.95 else "FAILURE"
                    failed_attempts = 0 if auth_status == "SUCCESS" else user_rng.randint(1, 3)
                    
                    event = RawLoginEvent(
                        user_id=user,
                        ip_address=user_ip,
                        latitude=loc["lat"],
                        longitude=loc["lon"],
                        location=loc["loc"],
                        device_fingerprint=self._generate_device(user),
                        user_agent="Mozilla/5.0 (Synthetic)",
                        timestamp=event_time,
                        auth_status=auth_status,
                        failed_attempts=failed_attempts,
                        access_pattern="DIRECT",
                        source_event_id=str(uuid.uuid4()),
                        source="GENERATOR"
                    )
                    events.append(event)
                    
        # Sort by timestamp
        events.sort(key=lambda x: x.timestamp)
        return events
