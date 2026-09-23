"""ALIAS User History Service.

Reconstructs a user's historical authentication profile from persisted events.
Descriptive aggregates only. No security judgments.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any, List

from models.database import LoginEvent

class UserHistoryService:
    """Service to reconstruct user historical authentication aggregates."""

    @staticmethod
    def get_user_history(db: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Aggregate user historical events for the last N days.
        Returns baseline-ready features.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(LoginEvent).filter(
            LoginEvent.user_id == user_id,
            LoginEvent.timestamp >= cutoff_date
        )
        
        events = query.all()
        if not events:
            return {
                "user_id": user_id,
                "login_count": 0,
                "known_devices": [],
                "known_locations": [],
                "known_ips": [],
                "first_seen": None,
                "last_seen": None,
                "auth_distribution": {},
                "hourly_distribution": {}
            }
            
        known_devices = set()
        known_locations = set()
        known_ips = set()
        auth_dist = {"SUCCESS": 0, "FAILURE": 0}
        hourly_dist = {i: 0 for i in range(24)}
        
        first_seen = events[0].timestamp
        last_seen = events[0].timestamp
        
        for event in events:
            if event.device_fingerprint:
                known_devices.add(event.device_fingerprint)
            if event.location:
                known_locations.add(event.location)
            if event.ip_address:
                known_ips.add(event.ip_address)
                
            status = event.auth_status.upper()
            if status in auth_dist:
                auth_dist[status] += 1
            else:
                auth_dist[status] = 1
                
            hourly_dist[event.timestamp.hour] += 1
            
            if event.timestamp < first_seen:
                first_seen = event.timestamp
            if event.timestamp > last_seen:
                last_seen = event.timestamp
                
        return {
            "user_id": user_id,
            "login_count": len(events),
            "known_devices": list(known_devices),
            "known_locations": list(known_locations),
            "known_ips": list(known_ips),
            "first_seen": first_seen.isoformat(),
            "last_seen": last_seen.isoformat(),
            "auth_distribution": auth_dist,
            "hourly_distribution": hourly_dist
        }
