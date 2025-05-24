from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


def validate_non_empty_string(v: Optional[str], field_name: str) -> Optional[str]:
    """Helper function to validate non-empty strings."""
    if v is not None and (not v or not v.strip()):
        raise ValueError(f"{field_name} cannot be empty or whitespace only")
    return v.strip() if v else v


class HerdBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the herd")
    location: str = Field(
        ..., min_length=1, max_length=200, description="Location of the herd"
    )

    @validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_non_empty_string(v, "Name")

    @validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        return validate_non_empty_string(v, "Location")


class HerdCreate(HerdBase):
    """Schema for creating a new herd."""

    pass


class HerdUpdate(BaseModel):
    """Schema for updating an existing herd."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Updated name of the herd"
    )
    location: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Updated location of the herd"
    )

    @validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        return validate_non_empty_string(v, "Name")

    @validator("location")
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        return validate_non_empty_string(v, "Location")


class Herd(HerdBase):
    """Schema for herd responses."""

    model_config = {"from_attributes": True}

    id: int = Field(..., description="Unique identifier for the herd")
    created_at: Optional[datetime] = Field(
        None, description="When the herd was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="When the herd was last updated"
    )


class HerdList(BaseModel):
    """Schema for paginated herd list responses."""

    items: list[Herd] = Field(..., description="List of herds")
    total: int = Field(..., description="Total number of herds")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items requested")


# Authentication schemas
class Token(BaseModel):
    """OAuth2 token response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data schema."""
    username: Optional[str] = Field(None, description="Username from token")


class User(BaseModel):
    """User schema."""
    username: str = Field(..., description="Username")
    disabled: Optional[bool] = Field(False, description="Whether user is disabled")


class UserInDB(User):
    """User schema for database storage."""
    hashed_password: str = Field(..., description="Hashed password")


# MCP Operation schemas
class MCPExecuteRequest(BaseModel):
    """Schema for MCP execute operation requests."""
    operation: str = Field(..., description="Operation to execute")
    parameters: Optional[dict] = Field(None, description="Operation parameters")


class MCPBroadcastRequest(BaseModel):
    """Schema for MCP broadcast operation requests."""
    message: str = Field(..., description="Message to broadcast")
    targets: Optional[list[str]] = Field(None, description="Target recipients")
