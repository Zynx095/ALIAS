"""ALIAS Baseline Preparation Service.

Transforms historical user aggregates into baseline-ready profiles
and persists them into the UserBaseline model.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models.database import UserBaseline, LoginEvent
from detection.baseline.engine import BaselineProfileEngine
import logging

logger = logging.getLogger("alias.services.baseline_prep")


class BaselinePreparationService:
    """Service to prepare and persist user baselines."""

    @staticmethod
    def prepare_baseline(db: Session, user_id: str, days: int = 30) -> UserBaseline:
        """
        Builds and persists a UserBaseline record from historical events.
        Includes all events (success and failure) to accurately build auth metrics.
        """
        logger.info(f"BASELINE_PREPARATION_STARTED: user={user_id} days={days}")

        # Fetch raw events for the engine
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        events = db.query(LoginEvent).filter(
            LoginEvent.user_id == user_id,
            LoginEvent.timestamp >= cutoff_date
        ).order_by(LoginEvent.timestamp.asc()).all()

        # Run the Baseline Profile Engine across all 6 models
        canonical_baseline = BaselineProfileEngine.compile_baseline(user_id, events)

        baseline = db.query(UserBaseline).filter(UserBaseline.user_id == user_id).first()
        if not baseline:
            baseline = UserBaseline(user_id=user_id)
            db.add(baseline)

        baseline.login_count = canonical_baseline.total_logins

        # Store the rich Pydantic models directly as JSON (dict) in the DB
        baseline.known_devices = canonical_baseline.device.model_dump(mode='json')
        baseline.known_ips = canonical_baseline.network.model_dump(mode='json')
        baseline.known_locations = canonical_baseline.location.model_dump(mode='json')
        baseline.typical_hours = canonical_baseline.temporal.model_dump(mode='json')
        baseline.auth_profile = canonical_baseline.authentication.model_dump(mode='json')
        baseline.access_patterns = canonical_baseline.access_pattern.model_dump(mode='json')

        baseline.status = canonical_baseline.status.value
        baseline.version = canonical_baseline.baseline_version

        if canonical_baseline.total_logins > 0:
            baseline.last_login_ip = canonical_baseline.network.last_seen_ip
            baseline.last_login_lat = canonical_baseline.location.last_seen_latitude
            baseline.last_login_lon = canonical_baseline.location.last_seen_longitude
            baseline.last_login_timestamp = canonical_baseline.temporal.last_seen
            baseline.last_login_device = canonical_baseline.device.last_seen_device

        baseline.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(baseline)

        logger.info(f"BASELINE_PREPARATION_COMPLETED: user={user_id} logins={baseline.login_count}")
        return baseline
