"""Protected Application (Yukith Hub / Demo Portal) Authentication & Telemetry API.

Acts as the authentication boundary for the protected application.
Validates credentials, manages consecutive failed-attempt counters,
and delivers factual authentication telemetry to ALIAS via the real ingestion pipeline.
"""
from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime, timedelta, timezone
import uuid
import logging

from models.database import get_db, SessionLocal, LoginEvent
from schemas.ingestion import RawLoginEvent
from schemas.login import LoginEventDetail
from services.ingestion_service import IngestionService
from services.baseline_preparation_service import BaselinePreparationService
from api.events import broadcast_ingestion

logger = logging.getLogger("alias.api.portal")
router = APIRouter()

# In-memory consecutive failed login attempts tracker per user
_FAILED_ATTEMPTS_STORE: Dict[str, int] = {}

# Baseline seeding constants — must stay in sync with the "new_york" / "corporate_laptop"
# presets below so a baseline login at those presets never reads as anomalous.
BASELINE_HISTORY_DEPTH = 10
# Spread of business hours (UTC) to seed baseline logins across, so a live
# demo run at any reasonable hour of the day reads as "typical" rather than
# flagging every portal login as off-hours because the seed used one fixed hour.
BASELINE_BUSINESS_HOURS_UTC = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
_HOME_IP = "198.51.100.24"
_HOME_LOCATION = "New York, US"
_HOME_LAT = 40.7128
_HOME_LNG = -74.0060
_HOME_DEVICE_FINGERPRINT = "macbook-pro-corp-m3-001"
_HOME_DEVICE_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Canonical Demo Users & Passwords (passwords stay in this auth handler, NEVER passed to telemetry)
# All three share the same home IP/location/device as the "new_york" + "corporate_laptop"
# presets below, so their seeded baselines match the portal's own baseline preset exactly.
DEMO_CREDENTIALS = {
    "yukith": {
        "user_id": "yukith",
        "email": "yukith@acme.corp",
        "password": "YukithSecure2026!",
        "name": "Yukith M Joseph",
        "role": "Security Engineer",
        "default_ip": _HOME_IP,
        "default_device": _HOME_DEVICE_FINGERPRINT,
        "home_location": _HOME_LOCATION,
        "home_lat": _HOME_LAT,
        "home_lng": _HOME_LNG,
    },
    "sarah": {
        "user_id": "demo_sarah",
        "email": "sarah.connors@acme.corp",
        "password": "Password123!",
        "name": "Sarah Connors",
        "role": "VP Operations",
        "default_ip": _HOME_IP,
        "default_device": _HOME_DEVICE_FINGERPRINT,
        "home_location": _HOME_LOCATION,
        "home_lat": _HOME_LAT,
        "home_lng": _HOME_LNG,
    },
    "ceo": {
        "user_id": "demo_ceo",
        "email": "ceo@acme.corp",
        "password": "Executive2026!",
        "name": "Chief Executive Officer",
        "role": "Executive",
        "default_ip": _HOME_IP,
        "default_device": _HOME_DEVICE_FINGERPRINT,
        "home_location": _HOME_LOCATION,
        "home_lat": _HOME_LAT,
        "home_lng": _HOME_LNG,
    },
}

# Location Presets with real coordinates
LOCATION_PRESETS = {
    "new_york": {
        "name": "New York, US (Baseline)",
        "location": "New York, US",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ip_address": "198.51.100.24",
        "access_pattern": "DIRECT",
        "flag": "🇺🇸",
    },
    "tokyo": {
        "name": "Tokyo, Japan (Impossible Travel)",
        "location": "Tokyo, JP",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "ip_address": "203.0.113.88",
        "access_pattern": "DIRECT",
        "flag": "🇯🇵",
    },
    "london": {
        "name": "London, UK (Transatlantic)",
        "location": "London, GB",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "ip_address": "195.54.160.10",
        "access_pattern": "DIRECT",
        "flag": "🇬🇧",
    },
    "sydney": {
        "name": "Sydney, Australia",
        "location": "Sydney, AU",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "ip_address": "139.130.4.5",
        "access_pattern": "DIRECT",
        "flag": "🇦🇺",
    },
    "frankfurt": {
        "name": "Frankfurt, Germany",
        "location": "Frankfurt, DE",
        "latitude": 50.1109,
        "longitude": 8.6821,
        "ip_address": "80.158.20.4",
        "access_pattern": "DIRECT",
        "flag": "🇩🇪",
    },
    "tor_exit": {
        "name": "Tor Exit Node (Zurich, CH)",
        "location": "Zurich, CH",
        "latitude": 47.3769,
        "longitude": 8.5417,
        "ip_address": "185.220.101.5",
        "access_pattern": "TOR",
        "flag": "🧅",
    },
}

DEVICE_PRESETS = {
    "corporate_laptop": {
        "name": "Corporate MacBook (Baseline Known)",
        "fingerprint": "macbook-pro-corp-m3-001",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    },
    "personal_android": {
        "name": "Personal Android Device (Unseen)",
        "fingerprint": "samsung-galaxy-s24-unseen-99",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36",
    },
    "iphone_unseen": {
        "name": "Personal iPhone (Unseen)",
        "fingerprint": "iphone-16-pro-unseen-88",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    },
}


def _ensure_baseline_seeded(db: Session, user_id: str) -> None:
    """Seed deterministic baseline history for a known portal demo user.

    Without this, a demo user's first-ever portal login has no baseline to
    compare against, so NEW_DEVICE / IMPOSSIBLE_TRAVEL / UNSEEN_IP anomalies
    never fire during a live demo. Seeds business-hour logins at the shared
    home IP/location/device (matching the "new_york" + "corporate_laptop"
    presets) so any deviation from those presets reads as a real anomaly.
    Idempotent: skips once real history already exists for this user.
    """
    # Gate on successful-login count, matching BaselineProfileEngine's own
    # READY threshold — raw row count is not reliable once ad-hoc failed
    # attempts (e.g. brute-force demo clicks) are mixed into history.
    success_count = db.query(LoginEvent).filter(
        LoginEvent.user_id == user_id, LoginEvent.auth_status == "SUCCESS"
    ).count()
    if success_count >= BASELINE_HISTORY_DEPTH:
        return

    now = datetime.now(timezone.utc)
    to_seed = BASELINE_HISTORY_DEPTH - success_count
    for i in range(to_seed, 0, -1):
        hour = BASELINE_BUSINESS_HOURS_UTC[i % len(BASELINE_BUSINESS_HOURS_UTC)]
        past_time = (now - timedelta(days=to_seed - i + 1)).replace(
            hour=hour, minute=0, second=0, microsecond=0
        )
        evt = RawLoginEvent(
            user_id=user_id,
            ip_address=_HOME_IP,
            latitude=_HOME_LAT,
            longitude=_HOME_LNG,
            location=_HOME_LOCATION,
            device_fingerprint=_HOME_DEVICE_FINGERPRINT,
            user_agent=_HOME_DEVICE_UA,
            timestamp=past_time,
            auth_status="SUCCESS",
            failed_attempts=0,
            access_pattern="DIRECT",
            source_event_id=f"portal-baseline-{user_id}-{uuid.uuid4().hex[:8]}",
            source="PORTAL_BASELINE",
        )
        IngestionService.ingest_single(db, evt)

    BaselinePreparationService.prepare_baseline(db, user_id, days=30)
    logger.info(f"PORTAL_BASELINE_SEEDED: user={user_id} added={to_seed}")


class PortalLoginRequest(BaseModel):
    """Payload submitted by the protected application login form."""
    username: str = Field(..., description="Username or email attempted")
    password: str = Field(..., description="Password attempted (never saved to telemetry)")
    location_preset: Optional[str] = Field("new_york", description="Key for LOCATION_PRESETS")
    device_preset: Optional[str] = Field("corporate_laptop", description="Key for DEVICE_PRESETS")
    access_pattern_override: Optional[str] = None


class PortalLoginResponse(BaseModel):
    """Authentication result and telemetry acknowledgment."""
    success: bool
    auth_status: str
    user_id: str
    failed_attempts: int
    message: str
    event_id: Optional[int] = None
    telemetry_delivered: bool
    location: str
    ip_address: str


@router.get("/config")
def get_portal_config():
    """Returns available demo presets and current user states for the portal UI."""
    return {
        "users": [
            {
                "key": k,
                "user_id": v["user_id"],
                "email": v["email"],
                "name": v["name"],
                "role": v["role"],
                "demo_password": v["password"],
            }
            for k, v in DEMO_CREDENTIALS.items()
        ],
        "locations": [
            {"key": k, **v} for k, v in LOCATION_PRESETS.items()
        ],
        "devices": [
            {"key": k, **v} for k, v in DEVICE_PRESETS.items()
        ],
        "active_failures": _FAILED_ATTEMPTS_STORE,
    }


@router.post("/reset-counters")
def reset_portal_counters():
    """Resets all in-memory failed attempt counters."""
    _FAILED_ATTEMPTS_STORE.clear()
    return {"status": "ok", "message": "Portal failed attempt counters cleared."}


@router.post("/login", response_model=PortalLoginResponse)
async def portal_authenticate(
    login_req: PortalLoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Authenticates login attempt against demo user credentials,
    updates consecutive failure counters, and generates REAL
    RawLoginEvent security telemetry for ALIAS ingestion.
    """
    normalized_input = login_req.username.strip().lower()

    # Find matching demo account
    matched_account = None
    for key, cred in DEMO_CREDENTIALS.items():
        if normalized_input in (key, cred["user_id"].lower(), cred["email"].lower()):
            matched_account = cred
            break

    user_id = matched_account["user_id"] if matched_account else normalized_input
    expected_password = matched_account["password"] if matched_account else None

    # Determine authentication success or failure
    is_authenticated = expected_password is not None and login_req.password == expected_password

    # Update failed attempts counter
    prior_failures = _FAILED_ATTEMPTS_STORE.get(user_id, 0)
    if is_authenticated:
        auth_status = "SUCCESS"
        failed_attempts_to_report = prior_failures
        # Reset counter after successful login
        _FAILED_ATTEMPTS_STORE[user_id] = 0
        message = "Authentication successful. Access granted."
    else:
        auth_status = "FAILURE"
        _FAILED_ATTEMPTS_STORE[user_id] = prior_failures + 1
        failed_attempts_to_report = _FAILED_ATTEMPTS_STORE[user_id]
        message = f"Invalid credentials. Failed attempt #{failed_attempts_to_report} recorded."

    # Resolve location telemetry
    loc_data = LOCATION_PRESETS.get(login_req.location_preset, LOCATION_PRESETS["new_york"])
    dev_data = DEVICE_PRESETS.get(login_req.device_preset, DEVICE_PRESETS["corporate_laptop"])

    # Ensure a known demo user has baseline history before their first real
    # login so anomaly detection has something to compare against; otherwise
    # rebuild the baseline as usual (cheap no-op once history is sufficient).
    try:
        if matched_account is not None:
            _ensure_baseline_seeded(db, user_id)
        else:
            BaselinePreparationService.prepare_baseline(db, user_id)
    except Exception as e:
        logger.warning(f"Baseline prep check non-fatal: {e}")

    # Build factual ALIAS RawLoginEvent (Strictly NO password fields)
    source_event_id = f"portal-login-{uuid.uuid4().hex[:12]}"
    now_utc = datetime.now(timezone.utc)

    raw_event = RawLoginEvent(
        user_id=user_id,
        ip_address=loc_data["ip_address"],
        latitude=loc_data["latitude"],
        longitude=loc_data["longitude"],
        location=loc_data["location"],
        device_fingerprint=dev_data["fingerprint"],
        user_agent=dev_data["user_agent"],
        timestamp=now_utc,
        auth_status=auth_status,
        failed_attempts=failed_attempts_to_report,
        access_pattern=login_req.access_pattern_override or loc_data["access_pattern"],
        source_event_id=source_event_id,
        source="PROTECTED_PORTAL"
    )

    # Ingest event into ALIAS database & pipeline
    success, db_event, msg = IngestionService.ingest_single(db, raw_event)

    if success and db_event:
        # Broadcast via WebSocket into real-time SOC dashboard
        broadcast_payload = LoginEventDetail.model_validate(db_event).model_dump(mode='json')
        broadcast_payload["event_id"] = db_event.id
        background_tasks.add_task(broadcast_ingestion, request, broadcast_payload)

    return PortalLoginResponse(
        success=is_authenticated,
        auth_status=auth_status,
        user_id=user_id,
        failed_attempts=failed_attempts_to_report,
        message=message,
        event_id=db_event.id if db_event else None,
        telemetry_delivered=success,
        location=loc_data["location"],
        ip_address=loc_data["ip_address"],
    )
