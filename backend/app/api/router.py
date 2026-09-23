"""ALIAS API Router — Aggregates all route modules."""
from fastapi import APIRouter
from api.health import router as health_router
from api.events import router as events_router
from api.users import router as users_router
from api.system import router as system_router
from api.anomalies import router as anomalies_router
from api.risk import router as risk_router
from api.investigations import router as investigations_router
from api.scenarios import router as scenarios_router
from api.portal import router as portal_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(events_router, prefix="/events", tags=["Events"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(anomalies_router, tags=["Anomalies"])
api_router.include_router(risk_router, tags=["Risk"])
api_router.include_router(investigations_router, prefix="/investigations", tags=["Investigations"])
api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(scenarios_router)
api_router.include_router(portal_router, prefix="/portal", tags=["Portal"])
