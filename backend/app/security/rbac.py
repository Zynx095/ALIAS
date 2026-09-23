"""ALIAS Role-Based Access Control.

Preserved from ShadowGuard with cleanup.
"""
from fastapi import HTTPException, status, Depends
from security.auth import get_current_user
import logging

logger = logging.getLogger("alias.security.rbac")


def require_role(required_role: str):
    """FastAPI dependency that enforces a specific user role."""
    async def role_checker(user: dict | None = Depends(get_current_user)):
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return user
    return role_checker
