#!/usr/bin/env python3
"""
National Dairy Farm MCP Client

A client for interacting with the National Dairy Farm MCP Server.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import httpx
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DairyFarmMCPClient:
    """Client for National Dairy Farm MCP Server."""
    
    def __init__(
        self, 
        mcp_server_url: str = "http://localhost:8001",
        auth_token: Optional[str] = None
    ):
        self.mcp_server_url = mcp_server_url.rstrip("/")
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Default headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return {"error": str(e)}
    
    async def list_operations(self) -> List[Dict[str, Any]]:
        """List all available operations."""
        try:
            response = await self.client.get(
                f"{self.mcp_server_url}/operations",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Failed to list operations: {e}")
            return []
    
    async def execute_operation(
        self, 
        operation: str, 
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute an MCP operation."""
        if parameters is None:
            parameters = {}
        
        try:
            payload = {
                "operation": operation,
                "parameters": parameters
            }
            
            response = await self.client.post(
                f"{self.mcp_server_url}/execute",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Failed to execute operation: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check MCP server health."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/health")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class DairyFarmCLI:
    """Command-line interface for the Dairy Farm MCP Client."""
    
    def __init__(self, client: DairyFarmMCPClient):
        self.client = client
    
    async def show_server_info(self):
        """Display server information."""
        print("🐄 National Dairy Farm MCP Server Information")
        print("=" * 50)
        
        info = await self.client.get_server_info()
        if "error" in info:
            print(f"❌ Error: {info['error']}")
            return
        
        print(f"Name: {info.get('name', 'Unknown')}")
        print(f"Version: {info.get('version', 'Unknown')}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Operations: {info.get('operations_count', 0)}")
        print(f"API URL: {info.get('base_url', 'Unknown')}")
    
    async def list_operations(self):
        """List all available operations."""
        print("\n📋 Available Operations")
        print("=" * 30)
        
        operations = await self.client.list_operations()
        if not operations:
            print("No operations available or connection failed.")
            return
        
        # Group operations by category
        categories = {}
        for op in operations:
            # Extract category from operation name
            parts = op["name"].split("_")
            category = parts[0] if len(parts) > 1 else "general"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(op)
        
        for category, ops in categories.items():
            print(f"\n📂 {category.upper()}")
            print("-" * 20)
            for op in ops:
                print(f"  • {op['name']}")
                print(f"    {op['method']} {op['path']}")
                print(f"    {op['description']}")
                if op['parameters']:
                    print(f"    Parameters: {', '.join(op['parameters'])}")
                print()
    
    async def execute_operation(self, operation: str, parameters: Dict[str, Any]):
        """Execute a specific operation."""
        print(f"\n🔄 Executing: {operation}")
        print("-" * 30)
        
        result = await self.client.execute_operation(operation, parameters)
        
        if result.get("success"):
            print("✅ Operation successful!")
            if result.get("result"):
                print("\nResult:")
                print(json.dumps(result["result"], indent=2))
        else:
            print("❌ Operation failed!")
            if result.get("error"):
                print(f"Error: {result['error']}")
    
    async def health_check(self):
        """Check server health."""
        print("\n🏥 Health Check")
        print("-" * 15)
        
        health = await self.client.health_check()
        status = health.get("status", "unknown")
        
        if status == "healthy":
            print("✅ Server is healthy")
        else:
            print("❌ Server is unhealthy")
        
        print(f"Status: {status}")
        if "dairy_farm_api_connected" in health:
            api_status = "✅" if health["dairy_farm_api_connected"] else "❌"
            print(f"Dairy Farm API: {api_status}")
        
        if health.get("timestamp"):
            print(f"Timestamp: {health['timestamp']}")
        
        if health.get("error"):
            print(f"Error: {health['error']}")
    
    async def interactive_mode(self):
        """Run interactive mode."""
        print("\n🎯 Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print("-" * 40)
        
        while True:
            try:
                command = input("\nDairy Farm MCP> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() in ['help', 'h']:
                    await self.show_help()
                elif command.lower() in ['info', 'i']:
                    await self.show_server_info()
                elif command.lower() in ['list', 'l']:
                    await self.list_operations()
                elif command.lower() in ['health', 'status']:
                    await self.health_check()
                elif command.startswith('exec '):
                    await self.handle_exec_command(command[5:])
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit.")
            except EOFError:
                break
    
    async def show_help(self):
        """Show help information."""
        help_text = """
🆘 Available Commands:

Basic Commands:
  help, h          - Show this help
  info, i          - Show server information
  list, l          - List available operations
  health, status   - Check server health
  quit, exit, q    - Exit interactive mode

Operation Execution:
  exec <operation> [params]  - Execute an operation
  
Examples:
  exec list_farms
  exec get_farm farm_id=123
  exec create_farm name="New Farm" location="Iowa"
  exec list_evaluations farm_id=123 status=completed

Parameter Format:
  key=value key2="string value" key3=123
        """
        print(help_text)
    
    async def handle_exec_command(self, command_args: str):
        """Handle exec command with parameters."""
        parts = command_args.split()
        if not parts:
            print("Usage: exec <operation> [key=value ...]")
            return
        
        operation = parts[0]
        parameters = {}
        
        # Parse parameters
        for param in parts[1:]:
            if "=" in param:
                key, value = param.split("=", 1)
                # Try to parse as number
                try:
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                
                parameters[key] = value
            else:
                print(f"Invalid parameter format: {param}")
                return
        
        await self.execute_operation(operation, parameters)


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="National Dairy Farm MCP Client")
    parser.add_argument("--server", default="http://localhost:8001", 
                       help="MCP server URL")
    parser.add_argument("--token", help="Authentication token")
    parser.add_argument("--operation", help="Operation to execute")
    parser.add_argument("--parameters", help="Operation parameters (JSON)")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode")
    parser.add_argument("--info", action="store_true", help="Show server info")
    parser.add_argument("--list", action="store_true", help="List operations")
    parser.add_argument("--health", action="store_true", help="Check health")
    
    args = parser.parse_args()
    
    # Create client
    client = DairyFarmMCPClient(
        mcp_server_url=args.server,
        auth_token=args.token
    )
    
    cli = DairyFarmCLI(client)
    
    try:
        if args.interactive:
            await cli.interactive_mode()
        elif args.info:
            await cli.show_server_info()
        elif args.list:
            await cli.list_operations()
        elif args.health:
            await cli.health_check()
        elif args.operation:
            parameters = {}
            if args.parameters:
                try:
                    parameters = json.loads(args.parameters)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON parameters: {e}")
                    return
            
            await cli.execute_operation(args.operation, parameters)
        else:
            # Default: show server info
            await cli.show_server_info()
            print("\nUse --help for more options or --interactive for interactive mode")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())