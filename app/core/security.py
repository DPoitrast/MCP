"""Security utilities for authentication and authorization."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from jose import JWTError, jwt
except Exception:  # pragma: no cover - optional dependency

    class JWTError(Exception):
        pass

    class _JWT:
        def encode(self, payload, key, algorithm="HS256"):
            return "stub-token"

        def decode(self, token, key, algorithms=None):
            return {}

    jwt = _JWT()

from .config import settings
from ..exceptions import AuthenticationError

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise AuthenticationError("Invalid or expired token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Get the current authenticated user from the token."""
    token = credentials.credentials

    # For backwards compatibility, still accept the hardcoded token in development
    if settings.environment == "development" and token == "fake-super-secret-token":
        logger.warning("Using development token - not for production!")
        return {"sub": "development_user", "type": "development"}

    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Token missing user information")
        return payload
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency for routes that require authentication
CurrentUser = Depends(get_current_user)
