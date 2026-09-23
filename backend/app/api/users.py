"""User API endpoints for History and Baseline."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, UserBaseline
from services.user_history_service import UserHistoryService
from services.baseline_preparation_service import BaselinePreparationService

router = APIRouter()


@router.get("/{user_id}/history")
async def get_user_history(user_id: str, days: int = 30, db: Session = Depends(get_db)):
    """Retrieve historical authentication aggregates for a user."""
    return UserHistoryService.get_user_history(db, user_id, days)


@router.get("/{user_id}/baseline")
async def get_user_baseline(user_id: str, db: Session = Depends(get_db)):
    """Retrieve the current baseline profile for a user across all 6 behavioral dimensions."""
    baseline = db.query(UserBaseline).filter(UserBaseline.user_id == user_id).first()
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found for user")

    return {
        "user_id": baseline.user_id,
        "status": baseline.status,
        "version": baseline.version,
        "login_count": baseline.login_count,
        "known_devices": baseline.known_devices,
        "known_ips": baseline.known_ips,
        "known_locations": baseline.known_locations,
        "typical_hours": baseline.typical_hours,
        "auth_profile": baseline.auth_profile,
        "access_patterns": baseline.access_patterns,
        "last_login_timestamp": baseline.last_login_timestamp.isoformat() if baseline.last_login_timestamp else None,
        "updated_at": baseline.updated_at.isoformat()
    }


@router.post("/{user_id}/baseline/rebuild")
async def rebuild_user_baseline(user_id: str, days: int = 30, db: Session = Depends(get_db)):
    """Manually trigger a rebuild of the baseline for a user based on historical events."""
    baseline = BaselinePreparationService.prepare_baseline(db, user_id, days)
    return {
        "message": "Baseline rebuilt successfully",
        "user_id": baseline.user_id,
        "status": baseline.status,
        "version": baseline.version,
        "login_count": baseline.login_count
    }
