from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger("alias.exceptions")

class AliasException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class NotFoundError(AliasException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} '{identifier}' not found",
            status_code=404
        )

class ValidationError(AliasException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=422, details=details)

class DatabaseError(AliasException):
    def __init__(self, message: str = "A database error occurred"):
        super().__init__(code="DATABASE_ERROR", message=message, status_code=500)

async def alias_exception_handler(request: Request, exc: AliasException) -> JSONResponse:
    logger.error(f"{exc.code}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": {"errors": [{"field": e.get('loc', [])[-1] if e.get('loc') else 'unknown', "message": e.get('msg', '')} for e in errors]}}}
    )

async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An internal server error occurred", "details": {}}}
    )
