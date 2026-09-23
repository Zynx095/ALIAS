"""Baseline Service — Manages user behavioral baselines.

STATUS: FOUNDATION ONLY
The baseline construction and comparison logic will be implemented in Phase 3.
"""
from sqlalchemy.orm import Session
from models.database import UserBaseline
from core.exceptions import NotFoundError
import logging

logger = logging.getLogger("alias.services.baseline")


class BaselineService:
    """Handles user behavioral baseline management."""

    @staticmethod
    def get_baseline(db: Session, user_id: str) -> UserBaseline | None:
        """Retrieve a user's behavioral baseline."""
        baseline = db.query(UserBaseline).filter(UserBaseline.user_id == user_id).first()
        if not baseline:
            raise NotFoundError("UserBaseline", user_id)
        return baseline

    @staticmethod
    def create_or_update_baseline(db: Session, user_id: str, **kwargs) -> UserBaseline:
        """Create or update a user baseline. Full implementation in Phase 3."""
        # TODO: Phase 3 — Implement baseline construction from login history
        baseline = db.query(UserBaseline).filter(UserBaseline.user_id == user_id).first()
        if not baseline:
            baseline = UserBaseline(user_id=user_id, **kwargs)
            db.add(baseline)
        else:
            for key, value in kwargs.items():
                if hasattr(baseline, key):
                    setattr(baseline, key, value)
        db.commit()
        db.refresh(baseline)
        logger.info(f"Baseline updated for user: {user_id}")
        return baseline
