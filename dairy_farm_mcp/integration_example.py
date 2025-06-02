#!/usr/bin/env python3
"""
Integration example showing how to use the National Dairy Farm MCP Server
with the existing OpenAI-powered MCP agent system.
"""

import asyncio
import sys
import os

# Add parent directory to path to import existing MCP components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.mcp_agent import MCPAgent
from dairy_farm_mcp.client import DairyFarmMCPClient


class EnhancedMCPAgent(MCPAgent):
    """Enhanced MCP Agent with National Dairy Farm integration."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize Dairy Farm MCP client
        self.dairy_farm_client = DairyFarmMCPClient(
            mcp_server_url="http://localhost:8001"
        )
        
        # Add dairy farm operations to the agent's capabilities
        self._add_dairy_farm_operations()
    
    def _add_dairy_farm_operations(self):
        """Add dairy farm operations to the agent's tool set."""
        dairy_farm_tools = [
            {
                "name": "dairy_farm_list_farms",
                "method": "POST",
                "path": "/dairy-farm/list-farms",
                "description": "List dairy farms with filtering and pagination",
                "parameters": ["page", "size", "search", "coop_id", "state"]
            },
            {
                "name": "dairy_farm_get_farm",
                "method": "POST", 
                "path": "/dairy-farm/get-farm",
                "description": "Get detailed information about a specific dairy farm",
                "parameters": ["farm_id"]
            },
            {
                "name": "dairy_farm_create_evaluation",
                "method": "POST",
                "path": "/dairy-farm/create-evaluation", 
                "description": "Create a new farm evaluation",
                "parameters": ["farm_id", "evaluator_id", "evaluation_type", "scheduled_date"]
            },
            {
                "name": "dairy_farm_list_evaluations",
                "method": "POST",
                "path": "/dairy-farm/list-evaluations",
                "description": "List farm evaluations with filtering",
                "parameters": ["farm_id", "status", "evaluator_id", "date_from", "date_to"]
            },
            {
                "name": "dairy_farm_search_farms",
                "method": "POST",
                "path": "/dairy-farm/search-farms",
                "description": "Search dairy farms using advanced filters",
                "parameters": ["q", "filters", "facets", "page", "size"]
            },
            {
                "name": "dairy_farm_get_analytics",
                "method": "POST",
                "path": "/dairy-farm/get-analytics",
                "description": "Get farm performance analytics and metrics",
                "parameters": ["farm_id", "metrics", "period", "aggregation"]
            }
        ]
        
        # Add to capabilities if they exist
        if hasattr(self, 'capabilities') and self.capabilities:
            if 'tools' not in self.capabilities:
                self.capabilities['tools'] = []
            self.capabilities['tools'].extend(dairy_farm_tools)
        
        # Add to context for fallback
        if hasattr(self, 'context'):
            if 'api' not in self.context:
                self.context['api'] = {'tools': []}
            elif 'tools' not in self.context['api']:
                self.context['api']['tools'] = []
            self.context['api']['tools'].extend(dairy_farm_tools)
    
    async def execute_dairy_farm_operation(self, operation: str, **kwargs) -> dict:
        """Execute a dairy farm operation through the MCP server."""
        return await self.dairy_farm_client.execute_operation(operation, kwargs)
    
    async def intelligent_dairy_farm_query(
        self, 
        user_request: str, 
        conversation_history: list = None
    ) -> dict:
        """Use OpenAI to understand user intent for dairy farm operations."""
        
        system_prompt = """You are an AI assistant that helps users interact with dairy farm data through the National Dairy FARM Program API.

Available dairy farm operations:
- list_farms: List and search dairy farms
- get_farm: Get detailed farm information  
- create_evaluation: Create farm evaluations
- list_evaluations: List farm evaluations
- search_farms: Advanced farm search with filters
- get_farm_analytics: Get farm performance metrics
- list_coops: List dairy cooperatives
- create_farm: Create new farm records

When users ask about dairy farms, evaluations, or farm data, respond with a JSON object containing:
- "action": "dairy_farm_operation"
- "operation": the specific operation to use
- "parameters": object with the required parameters
- "explanation": brief explanation of what you're doing

If the user asks a general question about dairy farming, respond normally as a helpful assistant."""

        try:
            # Use the existing OpenAI integration
            result = self.chat_with_openai(
                user_message=user_request,
                conversation_history=conversation_history or [],
                system_prompt=system_prompt,
                model="gpt-4o-mini"
            )
            
            assistant_response = result["response"]
            
            # Try to parse if this is a dairy farm operation request
            if "dairy_farm_operation" in assistant_response:
                import json
                try:
                    # Extract JSON from response
                    start = assistant_response.find("{")
                    end = assistant_response.rfind("}") + 1
                    if start != -1 and end != 0:
                        action_data = json.loads(assistant_response[start:end])
                        
                        if action_data.get("action") == "dairy_farm_operation":
                            operation = action_data.get("operation")
                            parameters = action_data.get("parameters", {})
                            explanation = action_data.get("explanation", "")
                            
                            # Execute the dairy farm operation
                            try:
                                mcp_result = await self.execute_dairy_farm_operation(
                                    operation, **parameters
                                )
                                
                                # Format the response
                                if mcp_result.get("success"):
                                    formatted_response = f"{explanation}\n\nResults:\n{json.dumps(mcp_result.get('result', {}), indent=2)}"
                                else:
                                    formatted_response = f"{explanation}\n\nError: {mcp_result.get('error', 'Unknown error')}"
                                
                                return {
                                    "response": formatted_response,
                                    "dairy_farm_result": mcp_result,
                                    "conversation_history": result["conversation_history"],
                                    "action_taken": {
                                        "operation": operation,
                                        "parameters": parameters
                                    }
                                }
                            except Exception as e:
                                error_response = f"{explanation}\n\nError executing dairy farm operation: {str(e)}"
                                return {
                                    "response": error_response,
                                    "error": str(e),
                                    "conversation_history": result["conversation_history"]
                                }
                except Exception:
                    # If parsing fails, treat as normal conversation
                    pass
            
            # Return normal chat response
            return {
                "response": assistant_response,
                "conversation_history": result["conversation_history"]
            }
            
        except Exception as e:
            return {
                "response": f"Error processing dairy farm query: {str(e)}",
                "error": str(e)
            }
    
    async def close(self):
        """Close connections."""
        await self.dairy_farm_client.close()


async def demo_integration():
    """Demonstrate the enhanced MCP agent with dairy farm integration."""
    print("🐄 Enhanced MCP Agent with Dairy Farm Integration")
    print("=" * 55)
    
    # Create enhanced agent
    agent = EnhancedMCPAgent(
        base_url="http://localhost:8000",  # Original MCP server
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    print(f"✓ Enhanced agent created")
    print(f"✓ Available tools: {len(agent.get_available_tools())}")
    
    # Test dairy farm operations
    test_queries = [
        "Show me a list of dairy farms",
        "What are the recent evaluations for farms in Wisconsin?",
        "Can you search for organic certified farms?",
        "Get analytics for farm ID 12345",
        "Tell me about dairy farming best practices"
    ]
    
    print("\n🧪 Testing intelligent dairy farm queries:")
    print("-" * 40)
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        
        try:
            result = await agent.intelligent_dairy_farm_query(query)
            response = result["response"]
            
            # Truncate long responses
            if len(response) > 200:
                response = response[:200] + "..."
            
            print(f"🤖 Agent: {response}")
            
            if result.get("action_taken"):
                action = result["action_taken"]
                print(f"🔧 Executed: {action['operation']} with {len(action['parameters'])} parameters")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Cleanup
    await agent.close()
    
    print("\n✅ Integration demo completed!")


async def main():
    """Main function."""
    print("🚀 National Dairy Farm MCP Integration Example")
    print("=" * 50)
    
    # Check if OpenAI key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set - some features will be limited")
    
    # Check if dairy farm MCP server is running
    try:
        client = DairyFarmMCPClient()
        health = await client.health_check()
        await client.close()
        
        if health.get("status") == "healthy":
            print("✅ Dairy Farm MCP Server is running")
        else:
            print("⚠️  Dairy Farm MCP Server is not healthy")
    except Exception as e:
        print(f"❌ Cannot connect to Dairy Farm MCP Server: {e}")
        print("   Please start it with: python server.py")
        return
    
    # Run integration demo
    await demo_integration()
    
    print("\n📚 Integration Guide:")
    print("1. Start the original MCP server: uvicorn app.main:app --reload")
    print("2. Start the Dairy Farm MCP server: python dairy_farm_mcp/server.py")
    print("3. Use the EnhancedMCPAgent for combined functionality")
    print("4. Ask natural language questions about dairy farms")


if __name__ == "__main__":
    asyncio.run(main())