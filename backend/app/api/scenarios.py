import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.database import get_db, LoginEvent, UserBaseline, AnomalyRecord, RiskAssessment, InvestigationReport
from schemas.scenario import ScenarioMetadata, ScenarioStatusResponse
from services.scenarios.scenario_service import ScenarioService
from api.events import ingest_login_event

logger = logging.getLogger("alias.api.scenarios")
router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.get("", response_model=List[ScenarioMetadata])
def list_scenarios():
    """List all available deterministic demo scenarios."""
    scenarios = ScenarioService.get_available_scenarios()
    return [ScenarioMetadata(**s) for s in scenarios]

@router.post("/{scenario_id}/run", response_model=ScenarioStatusResponse)
async def run_scenario(
    scenario_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger a scenario. History is ingested quietly, test events are sent through the canonical pipeline."""
    try:
        user_id, test_events = ScenarioService.prepare_scenario(db, scenario_id)
        
        # Fire off the test events through the main ingestion pipeline endpoint logic 
        # so they emit WebSockets and process normally.
        # Since ingest_login_event is an endpoint function, we can just call it directly 
        # or emulate its background task queuing.
        
        from api.events import broadcast_ingestion
        from services.ingestion_service import IngestionService
        
        dispatched_event_ids = []
        for raw_evt in test_events:
            success, db_event, msg = IngestionService.ingest_single(db, raw_evt)
            if success:
                dispatched_event_ids.append(db_event.id)
                # Prepare payload
                event_dict = {
                    "event_id": db_event.id,
                    "user_id": db_event.user_id,
                    "ip_address": db_event.ip_address,
                    "location": db_event.location,
                    "latitude": db_event.latitude,
                    "longitude": db_event.longitude,
                    "timestamp": db_event.timestamp.isoformat(),
                    "auth_status": db_event.auth_status,
                    "access_pattern": db_event.access_pattern,
                }
                background_tasks.add_task(
                    broadcast_ingestion,
                    request,
                    event_dict
                )

        return ScenarioStatusResponse(
            status="Running",
            scenario_id=scenario_id,
            message="Scenario triggered successfully.",
            events_generated=len(test_events),
            results={"user_id": user_id, "event_ids": dispatched_event_ids}
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario {scenario_id} failed: {e}")
        raise HTTPException(status_code=500, detail="Internal scenario error")

@router.post("/reset", response_model=Dict[str, str])
def reset_demo_data(db: Session = Depends(get_db)):
    """Safely clear demo state (user_id starts with demo_ or source DEMO_HISTORY/DEMO_TEST)."""
    try:
        demo_users = db.query(LoginEvent.user_id).filter(
            LoginEvent.user_id.like("demo_%")
        ).distinct().all()
        
        demo_user_ids = [u[0] for u in demo_users]
        
        if demo_user_ids:
            # Delete in order of dependencies (or let cascade handle if configured, but let's be explicit)
            db.query(InvestigationReport).filter(InvestigationReport.event_id.in_(
                db.query(LoginEvent.id).filter(LoginEvent.user_id.in_(demo_user_ids))
            )).delete(synchronize_session=False)
            
            db.query(RiskAssessment).filter(RiskAssessment.event_id.in_(
                db.query(LoginEvent.id).filter(LoginEvent.user_id.in_(demo_user_ids))
            )).delete(synchronize_session=False)
            
            db.query(AnomalyRecord).filter(AnomalyRecord.event_id.in_(
                db.query(LoginEvent.id).filter(LoginEvent.user_id.in_(demo_user_ids))
            )).delete(synchronize_session=False)
            
            db.query(UserBaseline).filter(UserBaseline.user_id.in_(demo_user_ids)).delete(synchronize_session=False)
            db.query(LoginEvent).filter(LoginEvent.user_id.in_(demo_user_ids)).delete(synchronize_session=False)
            
            db.commit()
            
        return {"status": "success", "message": "Demo environment reset."}
    except Exception as e:
        db.rollback()
        logger.error(f"Reset failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset demo data.")
