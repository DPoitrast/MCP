"""Security utilities for authentication and authorization."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from passlib.context import CryptContext

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
from ..schemas import User

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Temporary in-memory user database (should be moved to persistent storage later)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "disabled": False,
    },
    "alice": {
        "username": "alice", 
        "hashed_password": "$2b$12$gSvqqUPvlXP2tfVFaWK1Be7DlH.PKlbpjP8OaWrXY.FEWm9sKnDXC",  # wonderland
        "disabled": False,
    },
    "disabled_user": {
        "username": "disabled_user",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "disabled": True,
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[dict]:
    """Get user from database."""
    return fake_users_db.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user credentials."""
    user = get_user(username)
    if not user:
        logger.warning(f"Authentication failed: user '{username}' not found")
        return None
    if not verify_password(password, user["hashed_password"]):
        logger.warning(f"Authentication failed: invalid password for user '{username}'")
        return None
    if user.get("disabled", False):
        logger.warning(f"Authentication failed: user '{username}' is disabled")
        return None
    
    logger.info(f"User '{username}' authenticated successfully")
    return user


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


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get the current authenticated user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # For backwards compatibility, still accept the hardcoded token in development
    if settings.environment == "development" and token == "fake-super-secret-token":
        logger.warning("Using development token - not for production!")
        return {"sub": "development_user", "type": "development", "username": "development_user"}

    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token missing username (sub) claim")
            raise credentials_exception
    except AuthenticationError:
        logger.warning("Token verification failed")
        raise credentials_exception

    user = get_user(username)
    if user is None:
        logger.warning(f"User '{username}' from token not found in database")
        raise credentials_exception
    
    if user.get("disabled", False):
        logger.warning(f"User '{username}' is disabled")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return {"username": username, **user}


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current active user (wrapper for additional checks)."""
    if current_user.get("disabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User account is disabled"
        )
    return current_user


# Dependency for routes that require authentication
CurrentUser = Depends(get_current_user)
CurrentActiveUser = Depends(get_current_active_user)
