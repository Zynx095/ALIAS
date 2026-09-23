"""Common API response schemas."""
from pydantic import BaseModel
from datetime import datetime

class HealthResponse(BaseModel):
    status: str = "healthy"
    app_name: str = "ALIAS"
    version: str = "0.1.0"
    environment: str = "development"
    database: str = "connected"
    timestamp: datetime

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}

class ErrorResponse(BaseModel):
    error: ErrorDetail

class PaginatedResponse(BaseModel):
    items: list
    total: int
    skip: int
    limit: int
