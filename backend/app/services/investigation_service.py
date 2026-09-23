"""Investigation Service — Orchestrates AI Investigations (Phase 6)."""
import logging
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException

from models.database import LoginEvent, InvestigationReport
from investigation.engine import InvestigationEngine

logger = logging.getLogger("alias.services.investigation")


class InvestigationService:
    """Orchestrates AI-assisted forensic investigations."""

    @staticmethod
    def investigate_event(db: Session, event_id: int, force: bool = False) -> Optional[InvestigationReport]:
        """Trigger an AI investigation for a specific event."""
        # 1. Fetch Event
        event = db.query(LoginEvent).filter(LoginEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="LoginEvent not found")
            
        # 2. Investigate via Engine
        engine = InvestigationEngine(db)
        report = engine.evaluate_and_persist(event, force_reevaluate=force)
        
        return report

    @staticmethod
    def get_investigations(db: Session, skip: int = 0, limit: int = 50) -> list[InvestigationReport]:
        """Fetch historical investigations."""
        return db.query(InvestigationReport).order_by(InvestigationReport.created_at.desc()).offset(skip).limit(limit).all()
        
    @staticmethod
    def get_investigation_by_event(db: Session, event_id: int) -> Optional[InvestigationReport]:
        """Fetch investigation for a specific event."""
        return db.query(InvestigationReport).filter(InvestigationReport.event_id == event_id).first()
