"""Login Event API endpoints."""
from fastapi import APIRouter, Depends, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from models.database import get_db
from schemas.ingestion import RawLoginEvent, BatchLoginEventRequest, BatchIngestionResult
from schemas.login import LoginEventResponse, LoginEventDetail
from schemas.common import PaginatedResponse
from services.event_service import EventService
from services.investigation_service import InvestigationService
from services.ingestion_service import IngestionService
import logging
from typing import Optional

logger = logging.getLogger("alias.api.events")
router = APIRouter()

async def broadcast_ingestion(request: Request, event: dict):
    """Background task to broadcast ingested events and behavioral comparison."""
    ws_manager = getattr(request.app.state, "ws_manager", None)
    # 1. Broadcast raw ingestion
    if ws_manager:
        await ws_manager.broadcast_event(
            event_type="LOGIN_EVENT",
            event_id=event["event_id"],
            payload=event
        )
    
    # 2. Run behavioral comparison
    from models.database import SessionLocal, LoginEvent, UserBaseline
    from schemas.baseline import CanonicalBaseline, BaselineStatus
    from detection.baseline.feature_extractor import BehavioralFeatureExtractor
    from detection.baseline.comparison_engine import BaselineComparisonEngine
    from detection.baseline.deviation_evidence import DeviationEvidenceBuilder
    from services.anomaly_service import AnomalyService
    
    db_session = SessionLocal()
    try:
        db_event = db_session.query(LoginEvent).filter(LoginEvent.id == event["event_id"]).first()
        if db_event:
            features = BehavioralFeatureExtractor.extract_features(db_event)
            db_baseline = db_session.query(UserBaseline).filter(UserBaseline.user_id == db_event.user_id).first()
            
            if not db_baseline or db_baseline.status == BaselineStatus.NO_BASELINE:
                baseline = CanonicalBaseline(
                    user_id=db_event.user_id,
                    total_logins=0,
                    status=BaselineStatus.NO_BASELINE
                )
            else:
                baseline = CanonicalBaseline(
                    user_id=db_event.user_id,
                    total_logins=db_baseline.login_count,
                    temporal=db_baseline.typical_hours or {},
                    device=db_baseline.known_devices or {},
                    location=db_baseline.known_locations or {},
                    network=db_baseline.known_ips or {},
                    authentication=db_baseline.auth_profile or {},
                    access_pattern=db_baseline.access_patterns or {},
                    status=db_baseline.status,
                    baseline_version=db_baseline.version
                )
            
            features.baseline_version = baseline.baseline_version
            comparison_result = BaselineComparisonEngine.compare(features, baseline)
            evidence_report = DeviationEvidenceBuilder.build_evidence(comparison_result)
            
            # Broadcast the factual evidence report (Phase 3)
            if ws_manager:
                await ws_manager.broadcast_event(
                event_type="BEHAVIORAL_COMPARISON",
                event_id=db_event.id,
                payload=evidence_report.model_dump(mode='json')
            )
            
            logger.info(f"DEBUG BROADCAST: baseline_status={baseline.status}, comparison_status={comparison_result.comparison_status}, deviations={comparison_result.deviations.keys()}")
            
            # 3. Phase 4: Anomaly Detection Engine
            anomaly_response = AnomalyService.evaluate_and_persist(db_session, db_event, features, comparison_result, evidence_report)
            
            logger.info(f"DEBUG BROADCAST: DB URL used: {db_session.get_bind().url}")
            
            if anomaly_response.has_anomalies:
                if ws_manager:
                    await ws_manager.broadcast_event(
                    event_type="ANOMALY_DETECTED",
                    event_id=db_event.id,
                    payload=anomaly_response.model_dump(mode='json')
                )
                
            # 4. Phase 5: Risk Assessment Engine
            from datetime import timedelta
            from core.config import get_settings
            settings = get_settings()
            window_start = db_event.timestamp - timedelta(minutes=settings.CORRELATION_WINDOW_MINUTES)
            recent_events = db_session.query(LoginEvent).filter(
                LoginEvent.user_id == db_event.user_id,
                LoginEvent.id != db_event.id,
                LoginEvent.timestamp >= window_start,
                LoginEvent.timestamp <= db_event.timestamp
            ).order_by(LoginEvent.timestamp.desc()).all()
            
            from detection.risk.engine import risk_engine
            risk_response = risk_engine.evaluate_and_persist(db_session, db_event, anomaly_response.anomalies, recent_events)
            
            if ws_manager:
                await ws_manager.broadcast_event(
                event_type="RISK_ASSESSMENT",
                event_id=db_event.id,
                payload=risk_response.model_dump(mode='json')
            )
            
            # 5. Phase 6: AI Investigation
            # Only investigate if there's any risk, to save AI tokens, or if it's the mock provider,
            # we can run it regardless. Let's run it for all to populate the DB, or maybe just if risk > 0.
            if risk_response.risk_score > 0:
                from investigation.engine import InvestigationEngine
                inv_engine = InvestigationEngine(db_session)
                report = inv_engine.evaluate_and_persist(db_event)
                if report:
                    from schemas.investigation import InvestigationReportResponse
                    report_schema = InvestigationReportResponse.model_validate(report)
                    if ws_manager:
                        await ws_manager.broadcast_event(
                        event_type="INVESTIGATION_REPORT",
                        event_id=db_event.id,
                        payload=report_schema.model_dump(mode='json')
                    )
    finally:
        if 'db_session' in locals():
            db_session.close()

@router.post("/login", response_model=LoginEventResponse, status_code=201)
async def ingest_login_event(
    event_data: RawLoginEvent,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ingest a single login event."""
    # Ensure source is correctly set
    if not event_data.source:
        event_data.source = "API"
        
    success, db_event, msg = IngestionService.ingest_single(db, event_data)
    
    if success:
        # Broadcast the full event detail
        broadcast_payload = LoginEventDetail.model_validate(db_event).model_dump(mode='json')
        broadcast_payload["event_id"] = db_event.id
        background_tasks.add_task(broadcast_ingestion, request, broadcast_payload)
        
    return LoginEventResponse(
        status="accepted" if success else "ignored",
        event_id=db_event.id if db_event else None,
        user_id=event_data.user_id,
        processing_status="INGESTED",
        timestamp=db_event.timestamp if db_event else None,
        message=msg
    )

@router.post("/batch", response_model=BatchIngestionResult, status_code=201)
async def ingest_batch_events(
    batch: BatchLoginEventRequest,
    db: Session = Depends(get_db)
):
    """Ingest a batch of login events."""
    for event in batch.events:
        if not event.source:
            event.source = "API_BATCH"
            
    result = IngestionService.ingest_batch(db, batch.events)
    return result

@router.get("", response_model=PaginatedResponse)
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List login events with pagination."""
    if user_id:
        from models.database import LoginEvent
        query = db.query(LoginEvent).filter(LoginEvent.user_id == user_id)
        total = query.count()
        events = query.order_by(LoginEvent.timestamp.desc()).offset(skip).limit(limit).all()
    else:
        events, total = EventService.list_events(db, skip=skip, limit=limit)
        
    return PaginatedResponse(
        items=[LoginEventDetail.model_validate(e) for e in events],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{event_id}", response_model=LoginEventDetail)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific login event by ID."""
    event = EventService.get_event(db, event_id)
    return LoginEventDetail.model_validate(event)

@router.get("/{event_id}/investigation")
async def get_investigation(event_id: int):
    """Retrieve the investigation report for a login event."""
    result = InvestigationService.investigate(event_id)
    return result

@router.post("/{event_id}/behavioral-comparison")
async def execute_behavioral_comparison(event_id: int, db: Session = Depends(get_db)):
    """Execute behavioral baseline comparison for an ingested event."""
    from fastapi import HTTPException
    from models.database import LoginEvent, UserBaseline
    from schemas.baseline import CanonicalBaseline, BaselineStatus
    from detection.baseline.feature_extractor import BehavioralFeatureExtractor
    from detection.baseline.comparison_engine import BaselineComparisonEngine
    from detection.baseline.deviation_evidence import DeviationEvidenceBuilder

    event = db.query(LoginEvent).filter(LoginEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="LoginEvent not found")

    features = BehavioralFeatureExtractor.extract_features(event)

    db_baseline = db.query(UserBaseline).filter(UserBaseline.user_id == event.user_id).first()
    
    # Map DB UserBaseline to CanonicalBaseline
    if not db_baseline or db_baseline.status == BaselineStatus.NO_BASELINE:
        baseline = CanonicalBaseline(
            user_id=event.user_id,
            total_logins=0,
            status=BaselineStatus.NO_BASELINE
        )
    else:
        baseline = CanonicalBaseline(
            user_id=event.user_id,
            total_logins=db_baseline.login_count,
            temporal=db_baseline.typical_hours or {},
            device=db_baseline.known_devices or {},
            location=db_baseline.known_locations or {},
            network=db_baseline.known_ips or {},
            authentication=db_baseline.auth_profile or {},
            access_pattern=db_baseline.access_patterns or {},
            status=db_baseline.status,
            baseline_version=db_baseline.version
        )
        
    features.baseline_version = baseline.baseline_version

    comparison_result = BaselineComparisonEngine.compare(features, baseline)
    evidence_report = DeviationEvidenceBuilder.build_evidence(comparison_result)

    return evidence_report

