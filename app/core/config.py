"""Application configuration settings with enhanced validation and type safety."""

import os
from enum import Enum
from typing import List, Optional, Union
from pydantic import Field, validator, root_validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Supported application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    url: str = Field(default="sqlite:///mcp.db", env="DATABASE_URL")
    path: str = Field(default="mcp.db", env="DATABASE_PATH")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=0, env="DATABASE_MAX_OVERFLOW")
    
    @validator("pool_size")
    def validate_pool_size(cls, v):
        if v < 1:
            raise ValueError("Pool size must be at least 1")
        return v


class SecuritySettings(BaseSettings):
    """Security configuration."""
    secret_key: str = Field(default="", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        if not v:
            env = values.get("environment", "development")
            if env == Environment.PRODUCTION:
                raise ValueError("SECRET_KEY must be set in production environment")
            return "dev-secret-key-change-in-production"
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("access_token_expire_minutes")
    def validate_token_expiry(cls, v):
        if v < 1:
            raise ValueError("Token expiry must be at least 1 minute")
        return v


class CORSSettings(BaseSettings):
    """CORS configuration."""
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    allow_methods: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ALLOW_METHODS")
    allow_headers: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ALLOW_HEADERS")


class APISettings(BaseSettings):
    """API configuration."""
    v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    title: str = Field(default="MCP Server", env="API_TITLE")
    description: str = Field(default="Model Context Protocol Server - Production Ready", env="API_DESCRIPTION")
    version: str = Field(default="1.0.0", env="API_VERSION")
    docs_url: Optional[str] = Field(default="/docs", env="API_DOCS_URL")
    redoc_url: Optional[str] = Field(default="/redoc", env="API_REDOC_URL")


class PerformanceSettings(BaseSettings):
    """Performance configuration."""
    max_query_limit: int = Field(default=1000, env="MAX_QUERY_LIMIT")
    default_query_limit: int = Field(default=100, env="DEFAULT_QUERY_LIMIT")
    connection_timeout: float = Field(default=30.0, env="CONNECTION_TIMEOUT")
    request_timeout: float = Field(default=30.0, env="REQUEST_TIMEOUT")
    
    @validator("max_query_limit")
    def validate_max_limit(cls, v):
        if v < 1:
            raise ValueError("Max query limit must be at least 1")
        return v
    
    @validator("default_query_limit")
    def validate_default_limit(cls, v, values):
        max_limit = values.get("max_query_limit", 1000)
        if v < 1:
            raise ValueError("Default query limit must be at least 1")
        if v > max_limit:
            raise ValueError("Default query limit cannot exceed max query limit")
        return v


class Settings(BaseSettings):
    """Application configuration settings with enhanced validation."""

    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    
    # Nested configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    api: APISettings = Field(default_factory=APISettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    
    @root_validator
    def validate_environment_settings(cls, values):
        """Validate environment-specific settings."""
        env = values.get("environment")
        debug = values.get("debug")
        
        if env == Environment.PRODUCTION and debug:
            raise ValueError("Debug mode cannot be enabled in production")
        
        # Ensure production has stricter CORS settings
        if env == Environment.PRODUCTION:
            cors_settings = values.get("cors", {})
            if isinstance(cors_settings, CORSSettings):
                if "*" in cors_settings.allowed_origins:
                    raise ValueError("Wildcard CORS origins not allowed in production")
        
        return values
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING
    
    # Backward compatibility properties
    @property
    def database_url(self) -> str:
        return self.database.url
    
    @property
    def database_path(self) -> str:
        return self.database.path
    
    @property
    def secret_key(self) -> str:
        return self.security.secret_key
    
    @property
    def algorithm(self) -> str:
        return self.security.algorithm
    
    @property
    def access_token_expire_minutes(self) -> int:
        return self.security.access_token_expire_minutes
    
    @property
    def allowed_origins(self) -> List[str]:
        return self.cors.allowed_origins
    
    @property
    def api_v1_prefix(self) -> str:
        return self.api.v1_prefix
    
    @property
    def title(self) -> str:
        return self.api.title
    
    @property
    def description(self) -> str:
        return self.api.description
    
    @property
    def version(self) -> str:
        return self.api.version
    
    @property
    def max_query_limit(self) -> int:
        return self.performance.max_query_limit
    
    @property
    def default_query_limit(self) -> int:
        return self.performance.default_query_limit
    
    @property
    def connection_timeout(self) -> float:
        return self.performance.connection_timeout
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        use_enum_values = True


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
