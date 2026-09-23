"""API endpoints for AI Investigations."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models.database import get_db
from schemas.investigation import InvestigationReportResponse, InvestigationRequest
from services.investigation_service import InvestigationService

logger = logging.getLogger("alias.api.investigations")
router = APIRouter()

@router.get("/", response_model=List[InvestigationReportResponse])
def list_investigations(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve all investigation reports."""
    reports = InvestigationService.get_investigations(db, skip=skip, limit=limit)
    return reports

@router.get("/events/{event_id}", response_model=InvestigationReportResponse)
def get_event_investigation(event_id: int, db: Session = Depends(get_db)):
    """Retrieve investigation for a specific event."""
    report = InvestigationService.get_investigation_by_event(db, event_id)
    if not report:
        raise HTTPException(status_code=404, detail="Investigation not found for this event")
    return report

@router.post("/events/{event_id}/investigate", response_model=InvestigationReportResponse)
def trigger_investigation(event_id: int, req: InvestigationRequest, db: Session = Depends(get_db)):
    """Manually trigger or re-trigger an investigation for an event."""
    report = InvestigationService.investigate_event(db, event_id, force=req.force_reevaluate)
    if not report:
        raise HTTPException(status_code=500, detail="Failed to generate investigation report")
    return report
