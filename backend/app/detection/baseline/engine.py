"""ALIAS Baseline Profile Engine.

Orchestrates the individual behavior models (Temporal, Device, Location,
Network, Authentication, Access Pattern) to compile a unified CanonicalBaseline
from raw login history.
"""
from typing import List
from datetime import datetime

from models.database import LoginEvent
from schemas.baseline import CanonicalBaseline, BaselineStatus
from detection.baseline.temporal_model import TemporalBehaviorModel
from detection.baseline.device_model import DeviceBehaviorModel
from detection.baseline.location_model import LocationBehaviorModel
from detection.baseline.network_model import NetworkBehaviorModel
from detection.baseline.auth_model import AuthenticationBehaviorModel
from detection.baseline.access_model import AccessPatternModel

MINIMUM_HISTORY_THRESHOLD = 5

class BaselineProfileEngine:
    """Master engine to compute a canonical baseline from event history."""

    @staticmethod
    def compile_baseline(user_id: str, events: List[LoginEvent]) -> CanonicalBaseline:
        """Runs all 6 models against historical events to compile the canonical baseline."""

        if not events:
            return CanonicalBaseline(
                user_id=user_id,
                total_logins=0,
                status=BaselineStatus.NO_BASELINE,
                updated_at=datetime.utcnow()
            )

        # Build profiles
        temporal_profile = TemporalBehaviorModel.build_profile(events)
        device_profile = DeviceBehaviorModel.build_profile(events)
        location_profile = LocationBehaviorModel.build_profile(events)
        network_profile = NetworkBehaviorModel.build_profile(events)
        auth_profile = AuthenticationBehaviorModel.build_profile(events)
        access_profile = AccessPatternModel.build_profile(events)
        
        # Determine Status (Use ONLY successful logins for threshold counting)
        success_count = sum(1 for e in events if getattr(e, "auth_status", "SUCCESS").upper() == "SUCCESS")
        
        if success_count < MINIMUM_HISTORY_THRESHOLD:
            status = BaselineStatus.INSUFFICIENT_HISTORY
        else:
            status = BaselineStatus.READY

        baseline = CanonicalBaseline(
            user_id=user_id,
            total_logins=len(events),
            temporal=temporal_profile,
            device=device_profile,
            location=location_profile,
            network=network_profile,
            authentication=auth_profile,
            access_pattern=access_profile,
            status=status,
            updated_at=datetime.utcnow()
        )
        
        baseline.generate_version()
        return baseline
