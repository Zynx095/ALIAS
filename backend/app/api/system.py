"""System endpoints for data generation and scenarios."""
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Dict

from models.database import get_db
from data.generator import SyntheticDataGenerator
from scenarios.runner import ScenarioRunner
from services.ingestion_service import IngestionService
from services.baseline_preparation_service import BaselinePreparationService
from schemas.ingestion import BatchIngestionResult

router = APIRouter()

@router.post("/generate/history", response_model=BatchIngestionResult)
async def generate_history(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Generate and ingest synthetic historical dataset."""
    generator = SyntheticDataGenerator()
    events = generator.generate_history(days=days)
    
    result = IngestionService.ingest_batch(db, events)
    return result

@router.post("/generate/baselines")
async def generate_baselines(db: Session = Depends(get_db)):
    """Rebuild all baselines based on history."""
    from data.generator import USERS
    results = []
    for user in USERS:
        baseline = BaselinePreparationService.prepare_baseline(db, user)
        results.append({"user": user, "logins": baseline.login_count})
    return {"status": "success", "baselines": results}


@router.post("/scenarios/{scenario_id}")
async def run_scenario(
    scenario_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str = "sarah.connors@acme.corp",
    db: Session = Depends(get_db)
):
    """Run a scenario, ingest events, and broadcast them."""
    events = ScenarioRunner.get_scenario(scenario_id, user_id)
    
    # We could use batch ingestion, but single allows broadcasting easily in Phase 2
    accepted = []
    for event in events:
        success, db_event, msg = IngestionService.ingest_single(db, event)
        if success:
            accepted.append(db_event.id)
            payload = {
                "event_id": db_event.id,
                "user_id": db_event.user_id,
                "timestamp": db_event.timestamp.isoformat(),
                "status": "INGESTED"
            }
            if hasattr(request.app.state, 'ws_manager'):
                background_tasks.add_task(
                    request.app.state.ws_manager.broadcast_event,
                    "LOGIN_EVENT", db_event.id, payload
                )
                
    return {"status": "accepted", "scenario": scenario_id, "events_generated": len(events), "events_ingested": len(accepted)}
