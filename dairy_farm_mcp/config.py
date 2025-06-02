"""Configuration for National Dairy Farm MCP Server."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class DairyFarmConfig(BaseSettings):
    """Configuration settings for the Dairy Farm MCP Server."""
    
    # Dairy Farm API Configuration
    dairy_farm_api_url: str = "https://eval.nationaldairyfarm.com/dfdm/api"
    dairy_farm_client_id: Optional[str] = None
    dairy_farm_client_secret: Optional[str] = None
    
    # MCP Server Configuration
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8001
    mcp_server_title: str = "National Dairy Farm MCP Server"
    mcp_server_description: str = "Model Context Protocol server for National Dairy FARM Program API"
    mcp_server_version: str = "1.0.0"
    
    # API Configuration
    api_timeout: int = 30
    api_version: str = "3.2"
    max_retries: int = 3
    
    # Authentication
    token_refresh_threshold_minutes: int = 5
    
    # Logging
    log_level: str = "INFO"
    
    # Environment-specific settings
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "DAIRY_FARM_"
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
dairy_farm_config = DairyFarmConfig()
mcp_client_config = MCPClientConfig()


def get_dairy_farm_config() -> DairyFarmConfig:
    """Get Dairy Farm configuration."""
    return dairy_farm_config


def get_mcp_client_config() -> MCPClientConfig:
    """Get MCP client configuration."""
    return mcp_client_config