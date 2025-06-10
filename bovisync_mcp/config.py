"""Configuration for Bovisync MCP Server."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class BovisyncConfig(BaseSettings):
    """Configuration settings for the Bovisync MCP Server."""
    
    # Bovisync API Configuration
    bovisync_api_url: str = "https://api.bovisync.com"
    bovisync_client_id: Optional[str] = None
    bovisync_client_secret: Optional[str] = None
    
    # MCP Server Configuration
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8002
    mcp_server_title: str = "Bovisync MCP Server"
    mcp_server_description: str = "Model Context Protocol server for Bovisync API"
    mcp_server_version: str = "1.0.0"
    
    # API Configuration
    api_timeout: int = 30
    max_retries: int = 3
    
    # Authentication
    token_refresh_threshold_minutes: int = 5
    oauth_scope: str = "animal:read event:read milktest:read parlor:read data:read"
    
    # Logging
    log_level: str = "INFO"
    
    # Environment-specific settings
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "BOVISYNC_"
        case_sensitive = False


class MCPClientConfig(BaseSettings):
    """Configuration for MCP clients connecting to this server."""
    
    # Client authentication (optional)
    require_client_auth: bool = False
    valid_client_tokens: list = []
    
    # Rate limiting
    requests_per_minute: int = 100
    burst_limit: int = 20
    
    class Config:
        env_file = ".env"
        env_prefix = "MCP_CLIENT_"
        case_sensitive = False


# Global configuration instances
bovisync_config = BovisyncConfig()
mcp_client_config = MCPClientConfig()


def get_bovisync_config() -> BovisyncConfig:
    """Get Bovisync configuration."""
    return bovisync_config


def get_mcp_client_config() -> MCPClientConfig:
    """Get MCP client configuration."""
    return mcp_client_config