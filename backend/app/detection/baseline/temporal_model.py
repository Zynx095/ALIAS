"""ALIAS Temporal Behavior Model.

Extracts time-of-day, day-of-week, and frequency characteristics
from a historical sequence of login events.
"""
from typing import List
from models.database import LoginEvent
from schemas.baseline import TemporalProfile

class TemporalBehaviorModel:
    """Models historical time-based authentication behavior."""
    
    @staticmethod
    def build_profile(events: List[LoginEvent]) -> TemporalProfile:
        """Constructs a TemporalProfile from historical events."""
        if not events:
            return TemporalProfile()
            
        hourly_dist = {str(i): 0 for i in range(24)}
        workday_count = 0
        weekend_count = 0
        
        first_seen = events[0].timestamp
        last_seen = events[0].timestamp
        
        for event in events:
            ts = event.timestamp
            
            # Update bounds
            if ts < first_seen:
                first_seen = ts
            if ts > last_seen:
                last_seen = ts
                
            # Hourly bucket
            hour_str = str(ts.hour)
            hourly_dist[hour_str] += 1
            
            # Workday vs Weekend (Monday=0, Sunday=6)
            if ts.weekday() >= 5:
                weekend_count += 1
            else:
                workday_count += 1
                
        # Determine typical hours (hours with > 5% of total volume)
        total_events = len(events)
        typical_hours = []
        if total_events > 0:
            threshold = total_events * 0.05
            for h, count in hourly_dist.items():
                if count >= threshold:
                    typical_hours.append(int(h))
        
        return TemporalProfile(
            hourly_distribution=hourly_dist,
            workday_count=workday_count,
            weekend_count=weekend_count,
            typical_hours=sorted(typical_hours),
            first_seen=first_seen,
            last_seen=last_seen
        )
