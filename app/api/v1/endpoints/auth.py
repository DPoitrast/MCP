"""Authentication endpoints."""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ....core.config import settings
from ....core.security import authenticate_user, create_access_token, CurrentUser
from ....schemas import Token, User, UserProfile # Added UserProfile
from ....models.user import AuthenticatedUserModel

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        form_data: OAuth2 password request form containing username and password
        
    Returns:
        Token: Access token and token type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"User '{user.username}' logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User, tags=["authentication"])
async def read_users_me(current_user: AuthenticatedUserModel = CurrentUser):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        User: Current user information
    """
    return User(username=current_user.username, disabled=current_user.disabled)


@router.get("/users/me/profile", response_model=UserProfile, tags=["authentication"]) # Added response_model
async def read_user_profile(current_user: AuthenticatedUserModel = CurrentUser):
    """
    Get detailed current user profile.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        dict: Detailed user profile information
    """
    return {
        "username": current_user.username,
        "disabled": current_user.disabled,
        "profile": {
            "user_type": current_user.user_type,
            "last_login": "Not tracked in development",
            "permissions": ["read", "write", "execute"] if not current_user.disabled else ["read"]
        }
    }