"""Agent configuration and settings."""

from typing import Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for the MCP agent."""
    
    # API Configuration
    base_url: str = Field(..., description="Base URL for the MCP API")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    
    # Discovery Configuration
    auto_discover: bool = Field(default=True, description="Enable automatic capability discovery")
    context_path: str = Field(default="model_context.yaml", description="Path to context file")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="Default OpenAI model")
    openai_temperature: float = Field(default=0.7, description="OpenAI temperature setting")
    openai_max_tokens: Optional[int] = Field(default=None, description="Max tokens for OpenAI responses")
    
    # Retry Configuration
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_requests: bool = Field(default=False, description="Log HTTP requests")
    
    class Config:
        env_prefix = "AGENT_"
        case_sensitive = False


class OpenAIConfig(BaseModel):
    """OpenAI-specific configuration."""
    
    api_key: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    class Config:
        env_prefix = "OPENAI_"