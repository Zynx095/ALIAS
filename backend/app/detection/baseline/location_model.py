"""ALIAS Location Behavior Model.

Extracts geographic norms, hubs, and coordinates from login events.
"""
from typing import List
from models.database import LoginEvent
from schemas.baseline import LocationProfile

class LocationBehaviorModel:
    """Models historical geographic location behavior."""
    
    @staticmethod
    def build_profile(events: List[LoginEvent]) -> LocationProfile:
        """Constructs a LocationProfile from historical events."""
        if not events:
            return LocationProfile()
            
        location_usage = {}
        last_seen_location = None
        last_seen_lat = None
        last_seen_lon = None
        
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        for event in sorted_events:
            loc = event.location
            if loc:
                location_usage[loc] = location_usage.get(loc, 0) + 1
                last_seen_location = loc
                last_seen_lat = event.latitude
                last_seen_lon = event.longitude
                
        # Primary locations: Making up > 20% of logins
        total_loc_events = sum(location_usage.values())
        primary_locations = []
        if total_loc_events > 0:
            threshold = total_loc_events * 0.20
            for loc, count in location_usage.items():
                if count >= threshold:
                    primary_locations.append(loc)
                    
        return LocationProfile(
            known_locations=list(location_usage.keys()),
            location_usage_counts=location_usage,
            primary_locations=primary_locations,
            last_seen_location=last_seen_location,
            last_seen_latitude=last_seen_lat,
            last_seen_longitude=last_seen_lon
        )
