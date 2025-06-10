"""User management service."""

import logging
from typing import Optional

from ..exceptions import UserNotFoundError, UserAlreadyExistsError # Import new exceptions

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations."""
    
    def __init__(self):
        """Initialize user service with development users."""
        # Development user database - in production, replace with proper database
        self._users_db = {
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
        logger.info(f"UserService initialized with {len(self._users_db)} development users")
    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username."""
        return self._users_db.get(username)
    
    def get_all_users(self) -> dict:
        """Get all users (for admin purposes)."""
        return self._users_db.copy()
    
    def create_user(self, username: str, hashed_password: str, disabled: bool = False) -> dict:
        """Create a new user."""
        if username in self._users_db:
            raise UserAlreadyExistsError(username) # Use custom exception
        
        user_data = {
            "username": username,
            "hashed_password": hashed_password,
            "disabled": disabled,
        }
        self._users_db[username] = user_data
        logger.info(f"Created new user: {username}")
        return user_data
    
    def update_user(self, username: str, **updates) -> Optional[dict]:
        """Update user information."""
        if username not in self._users_db:
            raise UserNotFoundError(username) # Use custom exception
        
        allowed_fields = {"hashed_password", "disabled"}
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        self._users_db[username].update(filtered_updates)
        logger.info(f"Updated user: {username}")
        return self._users_db[username]
    
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username in self._users_db:
            del self._users_db[username]
            logger.info(f"Deleted user: {username}")
            return True
        return False


# Global user service instance
user_service = UserService()