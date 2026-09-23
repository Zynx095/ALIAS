"""ALIAS Ingestion Service.

The canonical ingestion pipeline for login events.
Handles Validation -> Normalization -> Enrichment -> Idempotency -> Persistence.
"""
import hashlib
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from schemas.ingestion import RawLoginEvent, BatchIngestionResult
from services.normalization_service import NormalizationService
from services.enrichment_service import EnrichmentService
from models.database import LoginEvent

logger = logging.getLogger("alias.services.ingestion")

class IngestionService:
    """Canonical ingestion pipeline for ALIAS events."""

    @staticmethod
    def _generate_event_hash(normalized_event: dict) -> str:
        """Generate deterministic identity for idempotency."""
        # Use source_event_id if available
        if normalized_event.get("source_event_id"):
            return hashlib.sha256(normalized_event["source_event_id"].encode()).hexdigest()
        
        # Fallback to stable fields hash
        stable_string = (
            f"{normalized_event['user_id']}|"
            f"{normalized_event['timestamp'].isoformat()}|"
            f"{normalized_event['ip_address']}|"
            f"{normalized_event['device_fingerprint']}|"
            f"{normalized_event['auth_status']}"
        )
        return hashlib.sha256(stable_string.encode()).hexdigest()

    @classmethod
    def ingest_single(cls, db: Session, raw_event: RawLoginEvent, skip_commit: bool = False) -> Tuple[bool, LoginEvent, str]:
        """
        Process a single event through the pipeline.
        Returns (success, db_event, message).
        """
        try:
            logger.info(f"INGESTION_STARTED: user={raw_event.user_id} source={raw_event.source}")
            
            # Validation happens automatically via Pydantic model
            logger.debug(f"VALIDATION_COMPLETED: user={raw_event.user_id}")

            # 1. Normalization
            normalized = NormalizationService.normalize(raw_event)
            logger.debug(f"NORMALIZATION_COMPLETED: user={raw_event.user_id}")
            
            # 2. Enrichment
            enriched = EnrichmentService.enrich(normalized)
            logger.debug(f"ENRICHMENT_COMPLETED: user={raw_event.user_id}")

            # 3. Idempotency Check
            event_hash = cls._generate_event_hash(enriched)
            
            existing = db.query(LoginEvent).filter(LoginEvent.event_hash == event_hash).first()
            if existing:
                logger.info(f"DUPLICATE_DETECTED: event_hash={event_hash}")
                return False, existing, "Duplicate event ignored"

            # 4. Persistence
            db_event = LoginEvent(
                user_id=enriched["user_id"],
                ip_address=enriched["ip_address"],
                latitude=enriched.get("latitude"),
                longitude=enriched.get("longitude"),
                location=enriched.get("location"),
                device_fingerprint=enriched.get("device_fingerprint"),
                user_agent=enriched.get("user_agent"),
                timestamp=enriched["timestamp"],
                auth_status=enriched["auth_status"],
                failed_attempts=enriched["failed_attempts"],
                access_pattern=enriched["access_pattern"],
                event_hash=event_hash,
                enriched_data=enriched.get("enriched_data", {}),
                processing_status="INGESTED"
            )
            
            db.add(db_event)
            if not skip_commit:
                db.commit()
                db.refresh(db_event)
            
            logger.info(f"EVENT_PERSISTED: id={db_event.id} user={db_event.user_id}")
            return True, db_event, "Ingested successfully"

        except Exception as e:
            if not skip_commit:
                db.rollback()
            logger.error(f"PROCESSING_FAILED: user={raw_event.user_id} error={str(e)}")
            raise e

    @classmethod
    def ingest_batch(cls, db: Session, raw_events: List[RawLoginEvent]) -> BatchIngestionResult:
        """
        Process a batch of events through the identical pipeline.
        Partial success is supported.
        """
        logger.info(f"BATCH_STARTED: size={len(raw_events)}")
        accepted = 0
        duplicates = 0
        rejected = 0
        event_ids = []
        errors = []

        for idx, raw in enumerate(raw_events):
            try:
                success, db_event, msg = cls.ingest_single(db, raw, skip_commit=True)
                if success:
                    db.flush() # Ensure we get an ID
                    accepted += 1
                    event_ids.append(db_event.id)
                else:
                    duplicates += 1
            except Exception as e:
                rejected += 1
                errors.append({"index": idx, "user": raw.user_id, "error": str(e)})

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            logger.error(f"BATCH_FAILED: Integrity error during commit: {str(e)}")
            raise ValueError("Batch persistence failed due to database integrity error.")
        
        logger.info(f"BATCH_COMPLETED: accepted={accepted} duplicates={duplicates} rejected={rejected}")
        return BatchIngestionResult(
            accepted=accepted,
            duplicates=duplicates,
            rejected=rejected,
            total=len(raw_events),
            event_ids=event_ids,
            errors=errors
        )
