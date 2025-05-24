import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # Database
    database_url: str = Field(default="sqlite:///mcp.db", env="DATABASE_URL")
    database_path: str = Field(default="mcp.db", env="DATABASE_PATH")

    # Security
    secret_key: str = Field(default="", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Configuration
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"], env="ALLOWED_ORIGINS")

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    title: str = "MCP Server"
    description: str = "Model Context Protocol Server - Production Ready"
    version: str = "1.0.0"

    # Performance
    max_query_limit: int = 1000
    default_query_limit: int = 100
    connection_timeout: float = 30.0

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default secret key for development if not provided
        if not self.secret_key:
            if self.environment == "development":
                self.secret_key = "dev-secret-key-change-in-production"
            else:
                raise ValueError("SECRET_KEY must be set in production environment")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
