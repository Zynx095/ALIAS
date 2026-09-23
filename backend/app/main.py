"""ALIAS — AI-assisted Login Anomaly Investigation System

Main FastAPI application entry point.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from core.config import get_settings
from core.logging import setup_logging
from core.exceptions import (
    AliasException,
    alias_exception_handler,
    validation_exception_handler,
    internal_exception_handler
)
from models.database import init_db
from api.router import api_router
from websocket.manager import ConnectionManager
import logging

# ============================================================
# Initialize
# ============================================================
logger = setup_logging()
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================
# Middleware
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Exception Handlers
# ============================================================
app.add_exception_handler(AliasException, alias_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)

# ============================================================
# Database Initialization
# ============================================================
init_db()
logger.info("Database initialized successfully")

# ============================================================
# WebSocket Manager
# ============================================================
manager = ConnectionManager()
app.state.ws_manager = manager

# ============================================================
# API Routes
# ============================================================
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "description": settings.APP_DESCRIPTION,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def root_health():
    """Quick health check at root level."""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


# ============================================================
# WebSocket Endpoint
# ============================================================
@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time alert WebSocket endpoint."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================
# Startup
# ============================================================
@app.on_event("startup")
async def startup_event():
    logger.info("="*60)
    logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"  {settings.APP_DESCRIPTION}")
    logger.info(f"  Environment: {settings.ENVIRONMENT}")
    logger.info(f"  Database: {settings.DATABASE_URL}")
    logger.info(f"  CORS Origins: {settings.CORS_ORIGINS}")
    logger.info("="*60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
