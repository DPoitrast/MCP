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

    class Config:
        from_attributes = True


class ProfileDetails(BaseModel):
    """Detailed user profile information."""
    user_type: Optional[str] = Field(None, description="Type of user account")
    last_login: Optional[str] = Field(None, description="Last login timestamp as string")
    permissions: list[str] = Field([], description="List of user permissions")

    class Config:
        from_attributes = True


class UserProfile(User):
    """User profile schema including detailed information."""
    profile: ProfileDetails


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


class MCPExecuteResponse(BaseModel):
    """Schema for MCP execute operation responses."""
    success: bool = Field(..., description="Whether the operation was successful")
    operation: str = Field(..., description="Operation that was executed")
    result: Optional[dict[str, any]] = Field(None, description="Result of the operation")
    executed_by: str = Field(..., description="Username who executed the operation")


class MCPBroadcastResult(BaseModel):
    """Detailed result of a broadcast operation."""
    message_id: str = Field(..., description="Unique ID for the broadcast message")
    message: str = Field(..., description="The broadcasted message content")
    targets: list[str] = Field(..., description="Intended targets of the broadcast")
    delivered_count: int = Field(..., description="Number of targets message was delivered to")
    failed_count: int = Field(..., description="Number of targets message failed to deliver to")
    timestamp: datetime = Field(..., description="Timestamp of the broadcast") # Changed to datetime
    broadcast_by: str = Field(..., description="Username who initiated the broadcast")


class MCPBroadcastResponse(BaseModel):
    """Schema for MCP broadcast operation responses."""
    success: bool = Field(..., description="Whether the broadcast was successful")
    broadcast_result: Optional[MCPBroadcastResult] = Field(None, description="Detailed result of the broadcast")


class MCPModelInfo(BaseModel):
    """Schema for individual MCP model information."""
    id: str = Field(..., description="Unique ID of the model")
    name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    description: Optional[str] = Field(None, description="Description of the model")
    capabilities: list[str] = Field([], description="Capabilities of the model")
    status: str = Field(..., description="Status of the model (e.g., active, maintenance)")

    class Config:
        from_attributes = True


class MCPModelsListResponse(BaseModel):
    """Schema for the list of available MCP models."""
    models: list[MCPModelInfo] = Field(..., description="List of available MCP models")
    total_count: int = Field(..., description="Total number of models")
    active_count: int = Field(..., description="Number of active models")
    requested_by: str = Field(..., description="Username who requested the list")


# Agent schemas
class AgentToolInfo(BaseModel):
    """Schema for individual agent tool information."""
    name: str = Field(..., description="Name of the tool")
    description: Optional[str] = Field(None, description="Description of the tool")
    # Assuming a generic structure for parameters, adjust if more specific details are known
    parameters: Optional[list[dict[str, any]]] = Field(None, description="Parameters the tool accepts")


class AgentToolsListResponse(BaseModel):
    """Schema for the list of available agent tools."""
    tools: list[AgentToolInfo] = Field(..., description="List of available agent tools")
    total_count: int = Field(..., description="Total number of tools")
    requested_by: str = Field(..., description="Username who requested the list")


class AgentStatusResponse(BaseModel):
    """Schema for the agent status response."""
    agent_initialized: bool = Field(..., description="Is the agent initialized?")
    status: str = Field(..., description="Operational status of the agent (e.g., operational, error)")
    openai_connected: Optional[bool] = Field(None, description="Is the agent connected to OpenAI?")
    mcp_base_url: Optional[str] = Field(None, description="Base URL for MCP operations")
    capabilities_discovered: Optional[bool] = Field(None, description="Have MCP capabilities been discovered?")
    tools_available: Optional[int] = Field(None, description="Number of tools available to the agent")
    error: Optional[str] = Field(None, description="Error message if status is 'error'")
