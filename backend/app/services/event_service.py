"""Event Service — Manages login event lifecycle."""
from sqlalchemy.orm import Session
from datetime import datetime
from models.database import LoginEvent
from schemas.login import LoginEventRequest
from core.exceptions import NotFoundError, DatabaseError
import logging

logger = logging.getLogger("alias.services.event")


class EventService:
    """Handles login event creation, retrieval, and listing."""

    @staticmethod
    def create_event(db: Session, request: LoginEventRequest) -> LoginEvent:
        """Persist a new login event to the database."""
        try:
            event = LoginEvent(
                user_id=request.user_id,
                ip_address=request.ip_address,
                latitude=request.latitude,
                longitude=request.longitude,
                location=request.location,
                device_fingerprint=request.device_fingerprint,
                user_agent=request.user_agent,
                timestamp=request.timestamp or datetime.utcnow(),
                auth_status=request.auth_status,
                failed_attempts=request.failed_attempts,
                access_pattern=request.access_pattern,
                processing_status="INGESTED"
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            logger.info(f"Login event created: id={event.id}, user={event.user_id}, ip={event.ip_address}")
            return event
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create login event: {e}")
            raise DatabaseError(f"Failed to create login event: {e}")

    @staticmethod
    def get_event(db: Session, event_id: int) -> LoginEvent:
        """Retrieve a single login event by ID."""
        event = db.query(LoginEvent).filter(LoginEvent.id == event_id).first()
        if not event:
            raise NotFoundError("LoginEvent", str(event_id))
        return event

    @staticmethod
    def list_events(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[LoginEvent], int]:
        """List login events with pagination."""
        total = db.query(LoginEvent).count()
        events = (
            db.query(LoginEvent)
            .order_by(LoginEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return events, total
