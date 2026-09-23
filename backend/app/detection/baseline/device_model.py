"""ALIAS Device Behavior Model.

Extracts device fingerprints and usage statistics from login events.
"""
from typing import List
from models.database import LoginEvent
from schemas.baseline import DeviceProfile

class DeviceBehaviorModel:
    """Models historical device usage behavior."""
    
    @staticmethod
    def build_profile(events: List[LoginEvent]) -> DeviceProfile:
        """Constructs a DeviceProfile from historical events."""
        if not events:
            return DeviceProfile()
            
        device_usage = {}
        last_seen_device = None
        
        # Sort events by timestamp ascending to reliably get last_seen
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        for event in sorted_events:
            fp = event.device_fingerprint
            if fp:
                device_usage[fp] = device_usage.get(fp, 0) + 1
                last_seen_device = fp
                
        # Primary devices: Devices making up at least 20% of logins
        total_events = sum(device_usage.values())
        primary_devices = []
        if total_events > 0:
            threshold = total_events * 0.20
            for fp, count in device_usage.items():
                if count >= threshold:
                    primary_devices.append(fp)
                    
        return DeviceProfile(
            known_devices=list(device_usage.keys()),
            device_usage_counts=device_usage,
            primary_devices=primary_devices,
            last_seen_device=last_seen_device
        )
