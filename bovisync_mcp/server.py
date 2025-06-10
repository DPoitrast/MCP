#!/usr/bin/env python3
"""
Bovisync MCP Server

A Model Context Protocol server for the Bovisync API.
Provides access to dairy farm animal management, events, and milk production data.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Sequence
from datetime import datetime, timedelta
import httpx
import base64

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


class BovisyncMCPServer:
    """MCP Server for Bovisync API."""
    
    def __init__(
        self, 
        base_url: str = "https://api.bovisync.com",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id or os.getenv("BOVISYNC_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("BOVISYNC_CLIENT_SECRET")
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.active_herd_id: Optional[str] = None
        
        # HTTP client for API requests
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Supported API endpoints and operations based on Bovisync API documentation
        self.endpoints = {
            # Authentication
            "get_token": {
                "method": "POST",
                "path": "/auth/token/",
                "description": "Gets an access token to authorize access to API endpoints",
                "parameters": [],
                "auth_required": False,
                "scope": None
            },
            
            # Session Management
            "get_active_herd": {
                "method": "GET",
                "path": "/session/herd/",
                "description": "Returns the active herd for the current session",
                "parameters": [],
                "auth_required": True,
                "scope": "authenticated"
            },
            "set_active_herd": {
                "method": "POST",
                "path": "/session/herd/",
                "description": "Sets the active herd(s) for the current session",
                "parameters": ["herd_id"],
                "auth_required": True,
                "scope": "authenticated"
            },
            
            # User Management
            "get_user_herds": {
                "method": "GET",
                "path": "/user/herds/",
                "description": "Returns a list of herds accessible to the authenticated OAuth client",
                "parameters": [],
                "auth_required": True,
                "scope": "authenticated"
            },
            
            # Animal Management
            "list_animals": {
                "method": "GET",
                "path": "/animal/list/",
                "description": "Returns a list of animals in the herd for the current session",
                "parameters": ["limit", "offset", "search", "active_only"],
                "auth_required": True,
                "scope": "animal:read"
            },
            "get_animal_data": {
                "method": "GET",
                "path": "/animal/data/",
                "description": "Returns animal report item data (restricted to single-farm session only)",
                "parameters": ["animal_id", "report_items", "date_from", "date_to"],
                "auth_required": True,
                "scope": "animal:read"
            },
            "get_animal_bulk": {
                "method": "GET",
                "path": "/animal/bulk/",
                "description": "Returns bulk data for animals in the herd for the current session",
                "parameters": ["limit", "offset", "modified_since"],
                "auth_required": True,
                "scope": "animal:read"
            },
            
            # Event Management
            "list_events": {
                "method": "GET",
                "path": "/event/list/",
                "description": "Returns a list of events in the herd (restricted to single-farm session only)",
                "parameters": ["limit", "offset", "event_type", "animal_id", "date_from", "date_to"],
                "auth_required": True,
                "scope": "event:read"
            },
            "get_event_meta": {
                "method": "GET",
                "path": "/event/meta/",
                "description": "Returns information about event types",
                "parameters": ["event_type_id"],
                "auth_required": True,
                "scope": "event:read"
            },
            "get_event_bulk": {
                "method": "GET",
                "path": "/event/bulk/",
                "description": "Returns a list of events in the herd for a specified month (single-farm session)",
                "parameters": ["year", "month", "event_type"],
                "auth_required": True,
                "scope": "event:read"
            },
            
            # Milk Data
            "get_milk_test_data": {
                "method": "GET",
                "path": "/milk_test/data/",
                "description": "Returns a list of milk data (e.g., DHI) in the herd (single-farm session)",
                "parameters": ["limit", "offset", "animal_id", "test_date_from", "test_date_to"],
                "auth_required": True,
                "scope": "milktest:read"
            },
            "get_parlor_daily_data": {
                "method": "GET",
                "path": "/parlor_daily/data/",
                "description": "Returns a list of parlor milk data in the herd (single-farm session)",
                "parameters": ["limit", "offset", "date_from", "date_to", "animal_id"],
                "auth_required": True,
                "scope": "parlor:read"
            },
            
            # Reporting
            "get_report_animal_data": {
                "method": "GET",
                "path": "/report/animal/data/",
                "description": "Returns animal report item data",
                "parameters": ["animal_id", "report_items", "date_from", "date_to"],
                "auth_required": True,
                "scope": "data:read"
            }
        }
    
    async def authenticate(self) -> bool:
        """Authenticate with the Bovisync API using OAuth2 client credentials."""
        if not self.client_id or not self.client_secret:
            logger.error("Client ID and secret required for authentication")
            return False
        
        # Check if token is still valid
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at - timedelta(minutes=5)):
            return True
        
        try:
            # Create Basic Auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {credentials_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            auth_data = {
                "grant_type": "client_credentials",
                "scope": "animal:read event:read milktest:read parlor:read data:read"
            }
            
            response = await self.client.post(
                f"{self.base_url}/auth/token/",
                data=auth_data,
                headers=headers
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info("Successfully authenticated with Bovisync API")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def make_request(
        self, 
        method: str, 
        path: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to the Bovisync API."""
        
        # Ensure authentication
        if not await self.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Bovisync API"
            )
        
        # Prepare headers
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if headers:
            request_headers.update(headers)
        
        # Make request
        url = f"{self.base_url}{path}"
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers
            )
            
            if response.status_code in [200, 201, 202, 204]:
                if response.content:
                    return response.json()
                else:
                    return {"status": "success", "message": f"{method} {path} completed"}
            else:
                error_detail = f"API request failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_detail += f" - {error_data}"
                except:
                    error_detail += f" - {response.text}"
                
                logger.error(error_detail)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to connect to Bovisync API: {e}"
            )
    
    def get_available_operations(self) -> List[Dict[str, Any]]:
        """Get list of all available MCP operations."""
        operations = []
        
        for op_name, op_config in self.endpoints.items():
            operations.append({
                "name": op_name,
                "method": op_config["method"],
                "path": op_config["path"],
                "description": op_config["description"],
                "parameters": op_config["parameters"],
                "scope": op_config["scope"]
            })
        
        return operations
    
    async def execute_operation(
        self, 
        operation_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific MCP operation."""
        
        if operation_name not in self.endpoints:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown operation: {operation_name}"
            )
        
        endpoint = self.endpoints[operation_name]
        method = endpoint["method"]
        path_template = endpoint["path"]
        
        # Extract path parameters
        path_params = {}
        query_params = {}
        body_data = None
        
        # Process parameters
        for key, value in parameters.items():
            if f"{{{key}}}" in path_template:
                path_params[key] = value
            elif method in ["POST", "PUT", "PATCH"] and key not in ["limit", "offset"]:
                if body_data is None:
                    body_data = {}
                body_data[key] = value
            else:
                query_params[key] = value
        
        # Build final path
        final_path = path_template
        for param_name, param_value in path_params.items():
            final_path = final_path.replace(f"{{{param_name}}}", str(param_value))
        
        # Make the request
        return await self.make_request(
            method=method,
            path=final_path,
            params=query_params if query_params else None,
            data=body_data
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global server instance
bovisync_server = BovisyncMCPServer()

# FastAPI app
app = FastAPI(
    title="Bovisync MCP Server",
    description="Model Context Protocol server for Bovisync API",
    version="1.0.0"
)

# Request/Response Models
class MCPOperation(BaseModel):
    operation: str = Field(..., description="Name of the operation to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")

class MCPResponse(BaseModel):
    success: bool
    operation: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class OperationInfo(BaseModel):
    name: str
    method: str
    path: str
    description: str
    parameters: List[str]
    scope: Optional[str] = None

# Dependency for authentication (optional for this MCP server)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate MCP client authentication."""
    # For this MCP server, we'll accept any bearer token
    # In production, you might want to validate against your own user system
    return {"token": credentials.credentials}

@app.get("/")
async def root():
    """MCP Server information."""
    return {
        "name": "Bovisync MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol server for Bovisync API",
        "operations_count": len(bovisync_server.endpoints),
        "base_url": bovisync_server.base_url
    }

@app.get("/operations", response_model=List[OperationInfo])
async def list_operations():
    """List all available MCP operations."""
    return bovisync_server.get_available_operations()

@app.post("/execute", response_model=MCPResponse)
async def execute_operation(
    request: MCPOperation,
    current_user: Dict = Depends(get_current_user)
):
    """Execute an MCP operation."""
    try:
        result = await bovisync_server.execute_operation(
            operation_name=request.operation,
            parameters=request.parameters
        )
        
        return MCPResponse(
            success=True,
            operation=request.operation,
            result=result
        )
        
    except HTTPException as e:
        return MCPResponse(
            success=False,
            operation=request.operation,
            error=f"HTTP {e.status_code}: {e.detail}"
        )
    except Exception as e:
        logger.error(f"Operation execution failed: {e}")
        return MCPResponse(
            success=False,
            operation=request.operation,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test authentication
        auth_status = await bovisync_server.authenticate()
        
        return {
            "status": "healthy" if auth_status else "unhealthy",
            "bovisync_api_connected": auth_status,
            "timestamp": datetime.now().isoformat(),
            "active_herd": bovisync_server.active_herd_id
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await bovisync_server.close()

def main():
    """Run the MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bovisync MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8002, help="Port to bind to")
    parser.add_argument("--bovisync-url", default="https://api.bovisync.com", 
                       help="Bovisync API base URL")
    parser.add_argument("--client-id", help="Bovisync API client ID")
    parser.add_argument("--client-secret", help="Bovisync API client secret")
    
    args = parser.parse_args()
    
    # Configure the global server instance
    global bovisync_server
    bovisync_server = BovisyncMCPServer(
        base_url=args.bovisync_url,
        client_id=args.client_id,
        client_secret=args.client_secret
    )
    
    print(f"🐄 Starting Bovisync MCP Server on {args.host}:{args.port}")
    print(f"🔗 Bovisync API: {args.bovisync_url}")
    print(f"📋 Available operations: {len(bovisync_server.endpoints)}")
    
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()