"""Agent interaction endpoints with OpenAI integration."""

import logging
import os
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel

from ....core.security import CurrentActiveUser
from ....models.user import AuthenticatedUserModel
from ....schemas import ( # Added agent response schemas
    AgentToolInfo, AgentToolsListResponse, AgentStatusResponse
)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))
from agent.mcp_agent import MCPAgent

logger = logging.getLogger(__name__)

router = APIRouter()

# Global agent instance
_agent_instance = None

def get_agent() -> MCPAgent:
    """Get or create the MCP agent instance."""
    global _agent_instance
    if _agent_instance is None:
        # Initialize with default settings - in production, these should come from config
        base_url = os.getenv("MCP_BASE_URL", "http://localhost:8000")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        _agent_instance = MCPAgent(
            base_url=base_url,
            openai_api_key=openai_api_key
        )
    return _agent_instance

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    system_prompt: Optional[str] = None
    model: str = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Dict[str, str]]
    usage: Optional[Dict[str, Any]] = None

class IntelligentQueryRequest(BaseModel):
    request: str
    conversation_history: Optional[List[Dict[str, str]]] = None

class IntelligentQueryResponse(BaseModel):
    response: str
    conversation_history: List[Dict[str, str]]
    mcp_result: Optional[Dict[str, Any]] = None
    action_taken: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AgentCapabilitiesResponse(BaseModel):
    openai_available: bool
    mcp_tools: List[Dict[str, Any]]
    agent_info: Dict[str, Any]

# Schemas for endpoints that were previously returning dicts
# Already defined in app/schemas.py:
# AgentToolsListResponse, AgentStatusResponse


@router.post("/chat", response_model=ChatResponse, tags=["agent"])
async def chat_with_agent(
    request: ChatRequest,
    current_user: AuthenticatedUserModel = CurrentActiveUser,
    agent: MCPAgent = Depends(get_agent) # Injected
):
    """
    Chat directly with the OpenAI-powered agent.
    
    This endpoint allows users to have a conversation with the agent
    without triggering MCP operations.
    
    Args:
        request: Chat request containing message and conversation history
        current_user: Current authenticated user
        agent: Injected MCPAgent instance
        
    Returns:
        ChatResponse: Agent's response and updated conversation history
    """
    logger.info(f"User '{current_user.username}' starting chat with agent")
    
    try:
        # agent = get_agent() # Removed, now injected
        
        result = agent.chat_with_openai(
            user_message=request.message,
            conversation_history=request.conversation_history,
            system_prompt=request.system_prompt,
            model=request.model
        )
        
        logger.info(f"Chat completed for user '{current_user.username}'")
        return ChatResponse(
            response=result["response"],
            conversation_history=result["conversation_history"],
            usage=result.get("usage")
        )
        
    except Exception as e:
        logger.error(f"Chat failed for user '{current_user.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.post("/query", response_model=IntelligentQueryResponse, tags=["agent"])
async def intelligent_query(
    request: IntelligentQueryRequest,
    current_user: AuthenticatedUserModel = CurrentActiveUser,
    authorization: str = Header(None),
    agent: MCPAgent = Depends(get_agent) # Injected
):
    """
    Make an intelligent query that can trigger MCP operations.
    
    This endpoint uses OpenAI to understand natural language requests
    and automatically execute appropriate MCP operations.
    
    Args:
        request: Query request containing natural language request
        current_user: Current authenticated user
        authorization: Bearer token for MCP operations
        agent: Injected MCPAgent instance
        
    Returns:
        IntelligentQueryResponse: Agent's response with potential MCP results
    """
    logger.info(f"User '{current_user.username}' making intelligent query")
    
    try:
        # agent = get_agent() # Removed, now injected
        
        # Extract token from authorization header
        token = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]  # Remove "Bearer " prefix
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token required for MCP operations"
            )
        
        result = agent.intelligent_mcp_query(
            user_request=request.request,
            token=token,
            conversation_history=request.conversation_history
        )
        
        logger.info(f"Intelligent query completed for user '{current_user.username}'")
        return IntelligentQueryResponse(
            response=result["response"],
            conversation_history=result["conversation_history"],
            mcp_result=result.get("mcp_result"),
            action_taken=result.get("action_taken"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Intelligent query failed for user '{current_user.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.get("/capabilities", response_model=AgentCapabilitiesResponse, tags=["agent"])
async def get_agent_capabilities(
    current_user: AuthenticatedUserModel = CurrentActiveUser,
    agent: MCPAgent = Depends(get_agent) # Injected
):
    """
    Get information about the agent's capabilities.
    
    Returns information about available OpenAI models, MCP tools,
    and general agent configuration.
    
    Args:
        current_user: Current authenticated user
        agent: Injected MCPAgent instance
        
    Returns:
        AgentCapabilitiesResponse: Agent capabilities and configuration
    """
    logger.info(f"User '{current_user.username}' requesting agent capabilities")
    
    try:
        # agent = get_agent() # Removed, now injected
        
        # Check OpenAI availability
        openai_available = agent.openai_client is not None
        
        # Get available MCP tools
        mcp_tools = agent.get_available_tools()
        
        # Agent info
        agent_info = {
            "base_url": agent.base_url,
            "api_prefix": agent.api_prefix,
            "timeout": agent.timeout,
            "has_capabilities": bool(agent.capabilities),
            "capabilities_count": len(agent.capabilities.get("tools", [])) if agent.capabilities else 0
        }
        
        return AgentCapabilitiesResponse(
            openai_available=openai_available,
            mcp_tools=mcp_tools,
            agent_info=agent_info
        )
        
    except Exception as e:
        logger.error(f"Failed to get agent capabilities for user '{current_user.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get capabilities: {str(e)}"
        )


@router.get("/tools", response_model=AgentToolsListResponse, tags=["agent"]) # Added response_model
async def list_available_tools(
    current_user: AuthenticatedUserModel = CurrentActiveUser,
    agent: MCPAgent = Depends(get_agent) # Injected
):
    """
    List all available MCP tools that the agent can use.
    
    Args:
        current_user: Current authenticated user
        agent: Injected MCPAgent instance
        
    Returns:
        dict: Available MCP tools and their descriptions
    """
    logger.info(f"User '{current_user.username}' requesting available tools")
    
    try:
        # agent = get_agent() # Removed, now injected
        tools = agent.get_available_tools()
        
        return {
            "tools": tools,
            "total_count": len(tools),
            "requested_by": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Failed to list tools for user '{current_user.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )


@router.get("/status", response_model=AgentStatusResponse, tags=["agent"]) # Added response_model
async def agent_status(
    current_user: AuthenticatedUserModel = CurrentActiveUser,
    agent: MCPAgent = Depends(get_agent) # Injected
):
    """
    Get the current status of the agent.
    
    Args:
        current_user: Current authenticated user
        agent: Injected MCPAgent instance
        
    Returns:
        dict: Agent status information
    """
    logger.info(f"User '{current_user.username}' requesting agent status")
    
    try:
        # agent = get_agent() # This call itself could fail if MCPAgent init fails (Removed, now injected)

        # Attempt to gather full status information
        openai_connected = agent.openai_client is not None
        tools_available = len(agent.get_available_tools()) # This could fail if capabilities not loaded

        status_info = AgentStatusResponse(
            agent_initialized=True, # If get_agent() succeeded, it's initialized
            openai_connected=openai_connected,
            mcp_base_url=agent.base_url,
            capabilities_discovered=bool(agent.capabilities),
            tools_available=tools_available,
            status="operational"
        )
        return status_info
        
    except Exception as e:
        logger.error(f"Failed to get agent status for user '{current_user.username}': {e}", exc_info=True)
        # Return a 503 status code, body will be auto-generated by FastAPI
        # or we can provide a specific one if needed, but AgentStatusResponse is for success.
        # For simplicity, let FastAPI handle the response for HTTPException.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Agent status unavailable: {str(e)}"
        )