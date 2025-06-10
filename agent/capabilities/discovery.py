"""Capability discovery for MCP endpoints."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


class CapabilityDiscovery:
    """Discover and manage MCP capabilities."""
    
    def __init__(self, base_url: str, api_prefix: str = "/api/v1", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix
        self.timeout = timeout
        self._cached_capabilities: Optional[Dict[str, Any]] = None
    
    def discover_capabilities(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Discover API capabilities through OpenAPI endpoint."""
        if self._cached_capabilities and not force_refresh:
            return self._cached_capabilities
        
        if not REQUESTS_AVAILABLE:
            logger.error("Requests library not available for capability discovery")
            return {}
        
        try:
            # Try to get OpenAPI spec
            openapi_url = f"{self.base_url}{self.api_prefix}/openapi.json"
            
            response = requests.get(openapi_url, timeout=self.timeout)
            response.raise_for_status()
            
            openapi_spec = response.json()
            capabilities = self._parse_openapi_spec(openapi_spec)
            
            self._cached_capabilities = capabilities
            logger.info(f"Discovered {len(capabilities.get('paths', {}))} API endpoints")
            
            return capabilities
        
        except requests.RequestException as e:
            logger.warning(f"Failed to discover capabilities via OpenAPI: {e}")
            return {}
        
        except Exception as e:
            logger.error(f"Capability discovery error: {e}")
            return {}
    
    def _parse_openapi_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAPI specification into capability format."""
        capabilities = {
            "info": spec.get("info", {}),
            "paths": {},
            "components": spec.get("components", {}),
            "servers": spec.get("servers", []),
        }
        
        # Parse paths
        for path, path_spec in spec.get("paths", {}).items():
            capabilities["paths"][path] = {}
            
            for method, method_spec in path_spec.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    capabilities["paths"][path][method.upper()] = {
                        "summary": method_spec.get("summary", ""),
                        "description": method_spec.get("description", ""),
                        "tags": method_spec.get("tags", []),
                        "parameters": self._parse_parameters(method_spec.get("parameters", [])),
                        "request_body": method_spec.get("requestBody"),
                        "responses": method_spec.get("responses", {}),
                        "security": method_spec.get("security", []),
                    }
        
        return capabilities
    
    def _parse_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse OpenAPI parameters."""
        parsed = []
        
        for param in parameters:
            parsed.append({
                "name": param.get("name"),
                "in": param.get("in"),
                "required": param.get("required", False),
                "schema": param.get("schema", {}),
                "description": param.get("description", ""),
            })
        
        return parsed
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from discovered capabilities."""
        capabilities = self.discover_capabilities()
        tools = []
        
        for path, methods in capabilities.get("paths", {}).items():
            for method, spec in methods.items():
                tool = {
                    "name": self._generate_tool_name(path, method, spec),
                    "method": method,
                    "path": path,
                    "description": spec.get("description") or spec.get("summary", ""),
                    "parameters": [p["name"] for p in spec.get("parameters", [])],
                    "tags": spec.get("tags", []),
                    "requires_auth": bool(spec.get("security")),
                }
                tools.append(tool)
        
        return tools
    
    def _generate_tool_name(self, path: str, method: str, spec: Dict[str, Any]) -> str:
        """Generate a tool name from path and method."""
        # Use operationId if available
        if "operationId" in spec:
            return spec["operationId"]
        
        # Generate from path and method
        path_parts = [part for part in path.split("/") if part and not part.startswith("{")]
        if path_parts:
            base_name = "_".join(path_parts)
            return f"{method.lower()}_{base_name}"
        
        return f"{method.lower()}_endpoint"
    
    def find_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Find a tool by its name."""
        tools = self.get_available_tools()
        return next((tool for tool in tools if tool["name"] == tool_name), None)
    
    def get_endpoint_info(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific endpoint."""
        capabilities = self.discover_capabilities()
        return capabilities.get("paths", {}).get(path, {}).get(method.upper())
    
    def clear_cache(self) -> None:
        """Clear cached capabilities."""
        self._cached_capabilities = None
        logger.debug("Capability cache cleared")