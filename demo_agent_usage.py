#!/usr/bin/env python3
"""Demo script showing how to use the OpenAI-enhanced MCP agent."""

import os
from agent.mcp_agent import MCPAgent


def demo_basic_agent():
    """Demonstrate basic agent functionality."""
    print("🤖 Basic Agent Demo")
    print("-" * 30)
    
    # Create agent
    agent = MCPAgent(
        base_url="http://localhost:8000",
        openai_api_key=os.getenv("OPENAI_API_KEY")  # Will work with or without
    )
    
    print(f"✓ Agent initialized")
    print(f"✓ OpenAI available: {agent.openai_client is not None}")
    print(f"✓ MCP tools discovered: {len(agent.get_available_tools())}")
    
    # List available tools
    print("\n📋 Available MCP Tools:")
    for tool in agent.get_available_tools()[:5]:  # Show first 5
        name = tool.get('name', 'Unknown')
        desc = tool.get('description', 'No description')
        print(f"   • {name}: {desc}")
    
    return agent


def demo_openai_chat(agent):
    """Demonstrate OpenAI chat functionality."""
    print("\n💬 OpenAI Chat Demo")
    print("-" * 30)
    
    if not agent.openai_client:
        print("⚠️  OpenAI not available - set OPENAI_API_KEY to test chat")
        return
    
    try:
        # Simple chat
        response = agent.chat_with_openai(
            user_message="Hello! Can you help me understand what MCP is?",
            system_prompt="You are a helpful assistant that explains technical concepts clearly.",
            model="gpt-4o-mini"
        )
        
        print("User: Hello! Can you help me understand what MCP is?")
        print(f"Agent: {response['response'][:200]}...")
        print(f"✓ Chat successful ({len(response['conversation_history'])} messages in history)")
        
    except Exception as e:
        print(f"❌ Chat failed: {e}")


def demo_intelligent_query(agent):
    """Demonstrate intelligent MCP query functionality."""
    print("\n🧠 Intelligent Query Demo")
    print("-" * 30)
    
    if not agent.openai_client:
        print("⚠️  OpenAI not available - set OPENAI_API_KEY to test intelligent queries")
        return
    
    # Mock token for demo (in real usage, this would be a valid JWT)
    mock_token = "demo-token"
    
    try:
        # Intelligent query that might trigger MCP operations
        response = agent.intelligent_mcp_query(
            user_request="Can you show me what tools are available?",
            token=mock_token
        )
        
        print("User: Can you show me what tools are available?")
        print(f"Agent: {response['response'][:200]}...")
        
        if response.get('action_taken'):
            print(f"✓ MCP action taken: {response['action_taken']}")
        
    except Exception as e:
        print(f"❌ Intelligent query failed: {e}")


def demo_api_usage():
    """Show how to use the new API endpoints."""
    print("\n🌐 API Usage Demo")
    print("-" * 30)
    
    print("New API endpoints available at:")
    print("  • POST /api/v1/agent/chat - Direct chat with OpenAI")
    print("  • POST /api/v1/agent/query - Intelligent MCP queries")
    print("  • GET  /api/v1/agent/capabilities - Agent capabilities")
    print("  • GET  /api/v1/agent/tools - Available MCP tools")
    print("  • GET  /api/v1/agent/status - Agent status")
    
    print("\nExample usage with curl:")
    print("""
    # Chat with the agent
    curl -X POST "http://localhost:8000/api/v1/agent/chat" \\
         -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
         -H "Content-Type: application/json" \\
         -d '{"message": "Hello, what can you help me with?"}'
    
    # Make an intelligent query
    curl -X POST "http://localhost:8000/api/v1/agent/query" \\
         -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
         -H "Content-Type: application/json" \\
         -d '{"request": "Show me all available herds"}'
    
    # Get agent status
    curl -X GET "http://localhost:8000/api/v1/agent/status" \\
         -H "Authorization: Bearer YOUR_JWT_TOKEN"
    """)


def main():
    """Run the demo."""
    print("🚀 OpenAI-Enhanced MCP Agent Demo")
    print("=" * 50)
    
    # Check for OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✓ OpenAI API key found (starts with: {openai_key[:10]}...)")
    else:
        print("⚠️  No OPENAI_API_KEY found - some features will be limited")
    
    print()
    
    try:
        # Demo basic functionality
        agent = demo_basic_agent()
        
        # Demo OpenAI features
        demo_openai_chat(agent)
        demo_intelligent_query(agent)
        
        # Show API usage
        demo_api_usage()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\n🔧 To get started:")
        print("1. Set your OPENAI_API_KEY environment variable")
        print("2. Start the server: uvicorn app.main:app --reload")
        print("3. Visit http://localhost:8000/docs to try the API")
        print("4. Use the /api/v1/agent/ endpoints to interact with the enhanced agent")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())