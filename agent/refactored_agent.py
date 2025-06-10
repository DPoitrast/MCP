"""Refactored MCP Agent with improved modularity and separation of concerns."""

import logging
import os
from typing import Any, Dict, List, Optional

from .core.config import AgentConfig, OpenAIConfig
from .clients.openai_client import OpenAIClient
from .parsers.yaml_parser import YAMLParser, ContextValidator
from .capabilities.discovery import CapabilityDiscovery

logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


class MCPAgent:
    """
    Enhanced MCP Agent with modular architecture.
    
    Features:
    - Modular component architecture
    - Enhanced error handling
    - Capability discovery
    - OpenAI integration
    - Configuration management
    """
    
    def __init__(
        self,
        base_url: str,
        context_path: str = "model_context.yaml",
        auto_discover: bool = True,
        api_prefix: str = "/api/v1",
        timeout: float = 30.0,
        openai_api_key: Optional[str] = None,
        config: Optional[AgentConfig] = None
    ):
        # Initialize configuration
        self.config = config or AgentConfig(
            base_url=base_url,
            context_path=context_path,
            auto_discover=auto_discover,
            api_prefix=api_prefix,
            timeout=timeout,
            openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize components
        self.capability_discovery = CapabilityDiscovery(
            base_url=self.config.base_url,
            api_prefix=self.config.api_prefix,
            timeout=self.config.timeout
        )
        
        self.openai_client: Optional[OpenAIClient] = None
        self._initialize_openai()
        
        # Context and capabilities
        self.context: Dict[str, Any] = {}
        self.capabilities: Dict[str, Any] = {}
        
        # Initialize context and capabilities
        self._initialize_context()
        self._initialize_capabilities()
    
    def _initialize_openai(self) -> None:
        """Initialize OpenAI client if configured."""
        if self.config.openai_api_key:
            try:
                openai_config = OpenAIConfig(
                    api_key=self.config.openai_api_key,
                    model=self.config.openai_model,
                    temperature=self.config.openai_temperature,
                    max_tokens=self.config.openai_max_tokens
                )
                self.openai_client = OpenAIClient(openai_config)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.info("No OpenAI API key provided, OpenAI features disabled")
    
    def _initialize_context(self) -> None:
        """Initialize context from configuration file."""
        try:
            raw_context = YAMLParser.parse_context(self.config.context_path)
            self.context = ContextValidator.validate_context(raw_context)
            logger.debug(f"Loaded context with {len(self.context.get('api', {}).get('tools', []))} tools")
        except Exception as e:
            logger.warning(f"Failed to load context: {e}")
            self.context = {"api": {"tools": []}}
    
    def _initialize_capabilities(self) -> None:
        """Initialize capabilities through discovery or context."""
        if self.config.auto_discover:
            try:
                self.capabilities = self.capability_discovery.discover_capabilities()
                if self.capabilities:
                    logger.info("Successfully discovered API capabilities")
                    return
            except Exception as e:
                logger.warning(f"Capability discovery failed: {e}")
        
        # Fallback to context-based capabilities
        logger.info("Using context-based capabilities")
        self.capabilities = {"tools": self.context.get("api", {}).get("tools", [])}
    
    @property
    def has_openai(self) -> bool:
        """Check if OpenAI client is available."""
        return self.openai_client is not None and self.openai_client.is_available
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools."""
        if "paths" in self.capabilities:
            # Use discovered capabilities
            return self.capability_discovery.get_available_tools()
        else:
            # Use context-based tools
            return self.context.get("api", {}).get("tools", [])
    
    def find_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Find a tool by name."""
        tools = self.get_available_tools()
        return next((tool for tool in tools if tool["name"] == tool_name), None)
    
    def list_herd(self, token: str) -> Any:
        """List herd using the appropriate tool."""
        tool = self.find_tool("listHerd")
        if not tool:
            raise ValueError("listHerd tool not found in model context")
        
        if "path" not in tool:
            raise ValueError("listHerd tool path not found")
        
        return self._make_request(
            method=tool.get("method", "GET"),
            path=tool["path"],
            token=token
        )
    
    def _make_request(
        self,
        method: str,
        path: str,
        token: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make an authenticated request to the MCP API."""
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Requests library not available")
        
        url = f"{self.config.base_url}{path}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {response.reason}")
            raise RuntimeError(f"HTTP error {response.status_code}: {response.reason}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise RuntimeError(f"Request error: {e}")
    
    def chat_with_openai(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Chat with OpenAI using the configured client."""
        if not self.has_openai:
            raise RuntimeError("OpenAI client not available")
        
        return self.openai_client.chat_with_openai(
            user_message=user_message,
            conversation_history=conversation_history,
            system_prompt=system_prompt,
            model=model
        )
    
    def intelligent_mcp_query(
        self,
        user_request: str,
        token: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process a user request intelligently using OpenAI and MCP tools."""
        if not self.has_openai:
            raise RuntimeError("OpenAI integration required for intelligent queries")
        
        # Analyze the request to determine appropriate action
        tools_context = self._build_tools_context()
        system_prompt = f"""
        You are an intelligent assistant that can help users interact with a dairy farm management system.
        
        Available tools and capabilities:
        {tools_context}
        
        Analyze the user's request and determine the most appropriate action. If the request requires
        accessing farm data, indicate which tool should be used and provide the reasoning.
        
        Respond in the following format:
        ANALYSIS: [your analysis of the request]
        ACTION: [recommended action - either "tool_call" or "direct_response"]
        TOOL: [if ACTION is "tool_call", specify which tool]
        RESPONSE: [your response to the user]
        """
        
        try:
            analysis_result = self.chat_with_openai(
                user_message=user_request,
                conversation_history=conversation_history,
                system_prompt=system_prompt
            )
            
            response_text = analysis_result["response"]
            
            # Parse the structured response
            if "ACTION: tool_call" in response_text and "TOOL:" in response_text:
                # Extract tool name and attempt to execute
                tool_line = next(line for line in response_text.split("\n") if line.startswith("TOOL:"))
                tool_name = tool_line.split(":", 1)[1].strip()
                
                try:
                    if tool_name == "listHerd":
                        mcp_result = self.list_herd(token)
                        
                        # Generate final response with data
                        final_response = self.chat_with_openai(
                            user_message=f"Based on this data: {mcp_result}, respond to: {user_request}",
                            conversation_history=conversation_history
                        )
                        
                        return {
                            "response": final_response["response"],
                            "conversation_history": final_response["conversation_history"],
                            "mcp_result": mcp_result,
                            "action_taken": {"tool": tool_name, "success": True}
                        }
                    
                    else:
                        # Tool not implemented
                        return {
                            "response": f"I identified that you need the '{tool_name}' tool, but it's not yet implemented.",
                            "conversation_history": analysis_result["conversation_history"],
                            "mcp_result": None,
                            "action_taken": {"tool": tool_name, "success": False, "reason": "not_implemented"}
                        }
                
                except Exception as e:
                    error_msg = f"I tried to use the '{tool_name}' tool but encountered an error: {str(e)}"
                    return {
                        "response": error_msg,
                        "conversation_history": analysis_result["conversation_history"],
                        "mcp_result": None,
                        "action_taken": {"tool": tool_name, "success": False, "reason": str(e)},
                        "error": str(e)
                    }
            
            else:
                # Direct response without tool usage
                return {
                    "response": analysis_result["response"],
                    "conversation_history": analysis_result["conversation_history"],
                    "mcp_result": None,
                    "action_taken": {"tool": None, "success": True}
                }
        
        except Exception as e:
            logger.error(f"Intelligent query processing failed: {e}")
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "conversation_history": conversation_history or [],
                "mcp_result": None,
                "action_taken": None,
                "error": str(e)
            }
    
    def _build_tools_context(self) -> str:
        """Build a context string describing available tools."""
        tools = self.get_available_tools()
        if not tools:
            return "No tools currently available."
        
        context_parts = []
        for tool in tools:
            description = tool.get("description", "No description available")
            parameters = tool.get("parameters", [])
            param_str = f" (parameters: {', '.join(parameters)})" if parameters else ""
            context_parts.append(f"- {tool['name']}: {description}{param_str}")
        
        return "\n".join(context_parts)
    
    def refresh_capabilities(self) -> None:
        """Refresh discovered capabilities."""
        if self.config.auto_discover:
            self.capability_discovery.clear_cache()
            self._initialize_capabilities()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "base_url": self.config.base_url,
            "openai_available": self.has_openai,
            "auto_discover": self.config.auto_discover,
            "tools_count": len(self.get_available_tools()),
            "context_loaded": bool(self.context.get("api", {}).get("tools")),
            "capabilities_discovered": "paths" in self.capabilities,
        }