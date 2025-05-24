"""JWT provider with proper dependency injection."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class JWTProvider(ABC):
    """Abstract JWT provider interface."""
    
    @abstractmethod
    def encode(self, payload: Dict[str, Any], key: str, algorithm: str = "HS256") -> str:
        """Encode a JWT token."""
        pass
    
    @abstractmethod
    def decode(self, token: str, key: str, algorithms: Optional[list] = None) -> Dict[str, Any]:
        """Decode a JWT token."""
        pass


class JoseJWTProvider(JWTProvider):
    """JWT provider using python-jose library."""
    
    def __init__(self):
        try:
            from jose import jwt, JWTError
            self.jwt = jwt
            self.JWTError = JWTError
            logger.info("Initialized JWT provider with python-jose")
        except ImportError as e:
            logger.error(f"Failed to import jose: {e}")
            raise ImportError("python-jose is required for JWT functionality")
    
    def encode(self, payload: Dict[str, Any], key: str, algorithm: str = "HS256") -> str:
        """Encode a JWT token using jose."""
        return self.jwt.encode(payload, key, algorithm=algorithm)
    
    def decode(self, token: str, key: str, algorithms: Optional[list] = None) -> Dict[str, Any]:
        """Decode a JWT token using jose."""
        if algorithms is None:
            algorithms = ["HS256"]
        try:
            return self.jwt.decode(token, key, algorithms=algorithms)
        except self.JWTError as e:
            raise ValueError(f"Invalid JWT token: {e}")


class StubJWTProvider(JWTProvider):
    """Stub JWT provider for development/testing."""
    
    def __init__(self):
        logger.warning("Using stub JWT provider - not suitable for production!")
    
    def encode(self, payload: Dict[str, Any], key: str, algorithm: str = "HS256") -> str:
        """Return a stub token for development."""
        return "dev-stub-token"
    
    def decode(self, token: str, key: str, algorithms: Optional[list] = None) -> Dict[str, Any]:
        """Return stub payload for development."""
        if token == "dev-stub-token":
            return {"sub": "development_user", "exp": datetime.utcnow() + timedelta(hours=1)}
        return {}


def create_jwt_provider() -> JWTProvider:
    """Factory function to create appropriate JWT provider."""
    try:
        return JoseJWTProvider()
    except ImportError:
        logger.warning("python-jose not available, using stub JWT provider")
        return StubJWTProvider()


# Global JWT provider instance
jwt_provider = create_jwt_provider()