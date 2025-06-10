"""OpenAI client wrapper with enhanced error handling."""

import logging
from typing import Any, Dict, List, Optional

from ..core.config import OpenAIConfig

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None


class OpenAIClient:
    """Enhanced OpenAI client with error handling and configuration."""
    
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.client: Optional[Any] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the OpenAI client."""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI package not available")
            return
        
        if not self.config.api_key:
            logger.warning("OpenAI API key not provided")
            return
        
        try:
            self.client = openai.OpenAI(api_key=self.config.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    @property
    def is_available(self) -> bool:
        """Check if OpenAI client is available and configured."""
        return self.client is not None
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a chat completion with error handling."""
        if not self.is_available:
            raise RuntimeError("OpenAI client not available")
        
        # Use config defaults if not specified
        model = model or self.config.model
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                **kwargs
            )
            
            return {
                "response": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API request failed: {e}")
    
    def chat_with_openai(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simplified chat interface."""
        if not self.is_available:
            raise RuntimeError("OpenAI client not available")
        
        # Build messages list
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            result = self.chat_completion(messages, model=model)
            
            # Update conversation history
            updated_history = (conversation_history or []).copy()
            updated_history.append({"role": "user", "content": user_message})
            updated_history.append({"role": "assistant", "content": result["response"]})
            
            return {
                "response": result["response"],
                "conversation_history": updated_history,
                "usage": result.get("usage"),
                "model": result.get("model"),
            }
        
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        if not self.is_available:
            return []
        
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if "gpt" in model.id]
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []