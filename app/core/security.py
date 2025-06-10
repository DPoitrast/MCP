"""Security utilities for authentication and authorization."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from passlib.context import CryptContext

from .jwt_provider import jwt_provider

from .config import settings
from ..exceptions import AuthenticationError
from ..schemas import User
from ..models.user import AuthenticatedUserModel

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Import user service for user management
from ..services.user import user_service


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[dict]:
    """Get user from user service."""
    return user_service.get_user(username)


def authenticate_user(username: str, password: str) -> Optional[AuthenticatedUserModel]:
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
    return AuthenticatedUserModel.from_db_user(user)


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
    encoded_jwt = jwt_provider.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt_provider.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except ValueError as e:
        logger.warning(f"Token verification failed: {e}")
        raise AuthenticationError("Invalid or expired token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUserModel:
    """Get the current authenticated user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # For backwards compatibility, still accept the hardcoded token in development
    # IMPORTANT: This is a security risk. Commenting out for review.
    # It's highly recommended to remove this and use standard authentication
    # flows even in development, or implement a secure dev-only token issuer.
    # if settings.environment == "development" and token == "fake-super-secret-token":
    #     logger.warning("Using development token - NOT FOR PRODUCTION! This backdoor should be removed.")
    #     return AuthenticatedUserModel.development_user()

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

    return AuthenticatedUserModel.from_db_user(user)


async def get_current_active_user(current_user: AuthenticatedUserModel = Depends(get_current_user)) -> AuthenticatedUserModel:
    """
    Get current active user.
    The 'active' (not disabled) check is performed in get_current_user.
    This function primarily serves as a distinct dependency if needed,
    or can be extended with further role/permission checks if necessary.
    """
    # The disabled check on the user model is already performed in get_current_user
    # after fetching the user from the database.
    # If current_user.disabled were True here due to some other logic after get_current_user
    # and before this, then this check might be useful. But as is, it's redundant
    # with the check performed on the source user data in get_current_user.
    # For now, simply returning the user, assuming get_current_user is the source of truth for 'active'.
    return current_user


# Dependency for routes that require authentication
CurrentUser = Depends(get_current_user)
CurrentActiveUser = Depends(get_current_active_user)
