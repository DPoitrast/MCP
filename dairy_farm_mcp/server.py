#!/usr/bin/env python3
"""
National Dairy Farm MCP Server

A Model Context Protocol server for the National Dairy FARM Program API.
Provides access to dairy farm management data, evaluations, and analytics.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Sequence
from datetime import datetime, timedelta
import httpx

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

class DairyFarmMCPServer:
    """MCP Server for National Dairy Farm API."""
    
    def __init__(
        self, 
        base_url: str = "https://eval.nationaldairyfarm.com/dfdm/api",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id or os.getenv("DAIRY_FARM_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("DAIRY_FARM_CLIENT_SECRET")
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # HTTP client for API requests
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Supported API endpoints and operations
        self.endpoints = {
            # OAuth & Authentication
            "oauth_token": {
                "method": "POST",
                "path": "/oauth/token",
                "description": "Obtain OAuth access token",
                "parameters": ["grant_type", "client_id", "client_secret", "scope"]
            },
            
            # Co-ops Management
            "list_coops": {
                "method": "GET", 
                "path": "/coops",
                "description": "List all cooperatives",
                "parameters": ["page", "size", "sort"]
            },
            "get_coop": {
                "method": "GET",
                "path": "/coops/{coop_id}",
                "description": "Get specific cooperative details",
                "parameters": ["coop_id"]
            },
            "create_coop": {
                "method": "POST",
                "path": "/coops",
                "description": "Create new cooperative",
                "parameters": ["name", "description", "contact_info"]
            },
            "update_coop": {
                "method": "PUT",
                "path": "/coops/{coop_id}",
                "description": "Update cooperative information",
                "parameters": ["coop_id", "name", "description", "contact_info"]
            },
            
            # Farms Management
            "list_farms": {
                "method": "GET",
                "path": "/farms",
                "description": "List all farms",
                "parameters": ["page", "size", "sort", "coop_id", "search"]
            },
            "get_farm": {
                "method": "GET",
                "path": "/farms/{farm_id}",
                "description": "Get specific farm details",
                "parameters": ["farm_id"]
            },
            "create_farm": {
                "method": "POST",
                "path": "/farms",
                "description": "Create new farm",
                "parameters": ["name", "location", "coop_id", "contact_info"]
            },
            "update_farm": {
                "method": "PUT",
                "path": "/farms/{farm_id}",
                "description": "Update farm information",
                "parameters": ["farm_id", "name", "location", "contact_info"]
            },
            "delete_farm": {
                "method": "DELETE",
                "path": "/farms/{farm_id}",
                "description": "Delete farm",
                "parameters": ["farm_id"]
            },
            
            # Facilities Management
            "list_facilities": {
                "method": "GET",
                "path": "/facilities",
                "description": "List farm facilities",
                "parameters": ["page", "size", "farm_id", "facility_type"]
            },
            "get_facility": {
                "method": "GET",
                "path": "/facilities/{facility_id}",
                "description": "Get facility details",
                "parameters": ["facility_id"]
            },
            "create_facility": {
                "method": "POST",
                "path": "/facilities",
                "description": "Create new facility",
                "parameters": ["farm_id", "name", "type", "capacity", "location"]
            },
            "update_facility": {
                "method": "PUT",
                "path": "/facilities/{facility_id}",
                "description": "Update facility",
                "parameters": ["facility_id", "name", "type", "capacity", "location"]
            },
            
            # Users Management
            "list_users": {
                "method": "GET",
                "path": "/users",
                "description": "List system users",
                "parameters": ["page", "size", "role", "coop_id"]
            },
            "get_user": {
                "method": "GET",
                "path": "/users/{user_id}",
                "description": "Get user details",
                "parameters": ["user_id"]
            },
            "create_user": {
                "method": "POST",
                "path": "/users",
                "description": "Create new user",
                "parameters": ["username", "email", "role", "coop_id", "permissions"]
            },
            "update_user": {
                "method": "PUT",
                "path": "/users/{user_id}",
                "description": "Update user information",
                "parameters": ["user_id", "username", "email", "role", "permissions"]
            },
            
            # Evaluations Management
            "list_evaluations": {
                "method": "GET",
                "path": "/evaluations",
                "description": "List farm evaluations",
                "parameters": ["page", "size", "farm_id", "status", "evaluator_id", "date_from", "date_to"]
            },
            "get_evaluation": {
                "method": "GET",
                "path": "/evaluations/{evaluation_id}",
                "description": "Get evaluation details",
                "parameters": ["evaluation_id"]
            },
            "create_evaluation": {
                "method": "POST",
                "path": "/evaluations",
                "description": "Create new evaluation",
                "parameters": ["farm_id", "evaluator_id", "evaluation_type", "scheduled_date", "notes"]
            },
            "update_evaluation": {
                "method": "PUT",
                "path": "/evaluations/{evaluation_id}",
                "description": "Update evaluation",
                "parameters": ["evaluation_id", "status", "results", "notes", "completion_date"]
            },
            "submit_evaluation": {
                "method": "POST",
                "path": "/evaluations/{evaluation_id}/submit",
                "description": "Submit completed evaluation",
                "parameters": ["evaluation_id", "results", "certifications"]
            },
            
            # Life Cycle Analysis (LCA)
            "list_lca_reports": {
                "method": "GET",
                "path": "/lca/reports",
                "description": "List LCA reports",
                "parameters": ["page", "size", "farm_id", "report_type", "year"]
            },
            "get_lca_report": {
                "method": "GET",
                "path": "/lca/reports/{report_id}",
                "description": "Get LCA report details",
                "parameters": ["report_id"]
            },
            "create_lca_report": {
                "method": "POST",
                "path": "/lca/reports",
                "description": "Create new LCA report",
                "parameters": ["farm_id", "report_type", "year", "data", "methodology"]
            },
            "update_lca_report": {
                "method": "PUT",
                "path": "/lca/reports/{report_id}",
                "description": "Update LCA report",
                "parameters": ["report_id", "data", "methodology", "status"]
            },
            
            # Attachments Management
            "list_attachments": {
                "method": "GET",
                "path": "/attachments",
                "description": "List document attachments",
                "parameters": ["page", "size", "entity_type", "entity_id", "file_type"]
            },
            "get_attachment": {
                "method": "GET",
                "path": "/attachments/{attachment_id}",
                "description": "Get attachment details",
                "parameters": ["attachment_id"]
            },
            "upload_attachment": {
                "method": "POST",
                "path": "/attachments",
                "description": "Upload new attachment",
                "parameters": ["entity_type", "entity_id", "file", "description", "tags"]
            },
            "delete_attachment": {
                "method": "DELETE",
                "path": "/attachments/{attachment_id}",
                "description": "Delete attachment",
                "parameters": ["attachment_id"]
            },
            
            # Search Operations
            "search_farms": {
                "method": "GET",
                "path": "/search/farms",
                "description": "Search farms using Solr",
                "parameters": ["q", "filters", "facets", "page", "size"]
            },
            "search_evaluations": {
                "method": "GET",
                "path": "/search/evaluations",
                "description": "Search evaluations",
                "parameters": ["q", "filters", "facets", "page", "size"]
            },
            
            # Analytics & Reporting
            "get_farm_analytics": {
                "method": "GET",
                "path": "/analytics/farms/{farm_id}",
                "description": "Get farm performance analytics",
                "parameters": ["farm_id", "metrics", "period", "aggregation"]
            },
            "get_coop_analytics": {
                "method": "GET",
                "path": "/analytics/coops/{coop_id}",
                "description": "Get cooperative analytics",
                "parameters": ["coop_id", "metrics", "period", "aggregation"]
            },
            "get_evaluation_trends": {
                "method": "GET",
                "path": "/analytics/evaluation-trends",
                "description": "Get evaluation trend analysis",
                "parameters": ["coop_id", "farm_id", "period", "metrics"]
            }
        }
    
    async def authenticate(self) -> bool:
        """Authenticate with the Dairy Farm API using OAuth2 client credentials."""
        if not self.client_id or not self.client_secret:
            logger.error("Client ID and secret required for authentication")
            return False
        
        # Check if token is still valid
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at - timedelta(minutes=5)):
            return True
        
        try:
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "read write"
            }
            
            response = await self.client.post(
                f"{self.base_url}/oauth/token",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info("Successfully authenticated with Dairy Farm API")
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
        """Make authenticated request to the Dairy Farm API."""
        
        # Ensure authentication
        if not await self.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Dairy Farm API"
            )
        
        # Prepare headers
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-accept-version": "3.2"  # API version
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
                detail=f"Failed to connect to Dairy Farm API: {e}"
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
                "parameters": op_config["parameters"]
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
            elif method in ["POST", "PUT", "PATCH"] and key not in ["page", "size", "sort"]:
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
dairy_farm_server = DairyFarmMCPServer()

# FastAPI app
app = FastAPI(
    title="National Dairy Farm MCP Server",
    description="Model Context Protocol server for the National Dairy FARM Program API",
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
        "name": "National Dairy Farm MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol server for National Dairy FARM Program API",
        "operations_count": len(dairy_farm_server.endpoints),
        "base_url": dairy_farm_server.base_url
    }

@app.get("/operations", response_model=List[OperationInfo])
async def list_operations():
    """List all available MCP operations."""
    return dairy_farm_server.get_available_operations()

@app.post("/execute", response_model=MCPResponse)
async def execute_operation(
    request: MCPOperation,
    current_user: Dict = Depends(get_current_user)
):
    """Execute an MCP operation."""
    try:
        result = await dairy_farm_server.execute_operation(
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
        auth_status = await dairy_farm_server.authenticate()
        
        return {
            "status": "healthy" if auth_status else "unhealthy",
            "dairy_farm_api_connected": auth_status,
            "timestamp": datetime.now().isoformat()
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
    await dairy_farm_server.close()

def main():
    """Run the MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="National Dairy Farm MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--dairy-farm-url", default="https://eval.nationaldairyfarm.com/dfdm/api", 
                       help="Dairy Farm API base URL")
    parser.add_argument("--client-id", help="Dairy Farm API client ID")
    parser.add_argument("--client-secret", help="Dairy Farm API client secret")
    
    args = parser.parse_args()
    
    # Configure the global server instance
    global dairy_farm_server
    dairy_farm_server = DairyFarmMCPServer(
        base_url=args.dairy_farm_url,
        client_id=args.client_id,
        client_secret=args.client_secret
    )
    
    print(f"🐄 Starting National Dairy Farm MCP Server on {args.host}:{args.port}")
    print(f"🔗 Dairy Farm API: {args.dairy_farm_url}")
    print(f"📋 Available operations: {len(dairy_farm_server.endpoints)}")
    
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()