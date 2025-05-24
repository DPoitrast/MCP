"""User domain models for type safety."""

from typing import Optional
from pydantic import BaseModel, Field


class UserModel(BaseModel):
    """Domain model for user data."""
    username: str = Field(..., description="Username")
    disabled: bool = Field(default=False, description="Whether user is disabled")
    
    class Config:
        frozen = True


class UserInDBModel(UserModel):
    """Domain model for user data stored in database."""
    hashed_password: str = Field(..., description="Hashed password")


class AuthenticatedUserModel(UserModel):
    """Domain model for authenticated user data."""
    user_type: str = Field(default="standard", description="User type")
    
    @classmethod
    def from_db_user(cls, db_user: dict) -> "AuthenticatedUserModel":
        """Create authenticated user from database user."""
        return cls(
            username=db_user["username"],
            disabled=db_user.get("disabled", False),
            user_type=db_user.get("type", "standard")
        )
    
    @classmethod
    def development_user(cls) -> "AuthenticatedUserModel":
        """Create development user for backwards compatibility."""
        return cls(
            username="development_user",
            disabled=False,
            user_type="development"
        )