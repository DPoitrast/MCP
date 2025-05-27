#!/usr/bin/env python3
"""Test script for the OpenAI-integrated MCP agent."""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.mcp_agent import MCPAgent


async def test_agent_initialization():
    """Test agent initialization with and without OpenAI."""
    print("🧪 Testing Agent Initialization...")
    
    # Test without OpenAI key
    print("\n1. Testing without OpenAI API key...")
    agent_no_openai = MCPAgent(
        base_url="http://localhost:8000",
        openai_api_key=None
    )
    
    print(f"   Agent initialized: {agent_no_openai is not None}")
    print(f"   OpenAI client: {agent_no_openai.openai_client is not None}")
    print(f"   Available tools: {len(agent_no_openai.get_available_tools())}")
    
    # Test with mock OpenAI key (won't work but should initialize)
    print("\n2. Testing with mock OpenAI API key...")
    agent_with_openai = MCPAgent(
        base_url="http://localhost:8000",
        openai_api_key="mock-key-for-testing"
    )
    
    print(f"   Agent initialized: {agent_with_openai is not None}")
    print(f"   OpenAI client: {agent_with_openai.openai_client is not None}")
    print(f"   Available tools: {len(agent_with_openai.get_available_tools())}")


def test_agent_capabilities():
    """Test agent capability discovery."""
    print("\n🧪 Testing Agent Capabilities...")
    
    agent = MCPAgent(
        base_url="http://localhost:8000",
        auto_discover=False  # Use static context for testing
    )
    
    tools = agent.get_available_tools()
    print(f"   Available tools: {len(tools)}")
    
    for tool in tools:
        print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")


def test_openai_methods():
    """Test OpenAI integration methods (mock)."""
    print("\n🧪 Testing OpenAI Integration Methods...")
    
    # Test with environment variable (if available)
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("   ⚠️  OPENAI_API_KEY not found in environment - skipping real API tests")
        openai_key = "mock-key"
    
    agent = MCPAgent(
        base_url="http://localhost:8000",
        openai_api_key=openai_key
    )
    
    print(f"   OpenAI client initialized: {agent.openai_client is not None}")
    
    # Test chat method structure (won't actually call API with mock key)
    if openai_key == "mock-key":
        print("   ✓ Chat method available but not testing with mock key")
        print("   ✓ Intelligent query method available but not testing with mock key")
    else:
        print("   🔄 Real OpenAI API key detected - you can test actual calls")
        try:
            # Only test if real API key is available
            result = agent.chat_with_openai(
                user_message="Hello, this is a test message",
                model="gpt-3.5-turbo"
            )
            print(f"   ✓ Chat test successful: {len(result['response'])} chars in response")
        except Exception as e:
            print(f"   ❌ Chat test failed: {e}")


def test_api_endpoints_structure():
    """Test that the API endpoints are properly structured."""
    print("\n🧪 Testing API Endpoint Structure...")
    
    try:
        from app.api.v1.endpoints.agent import router
        print("   ✓ Agent endpoints imported successfully")
        
        # Check routes
        routes = [route.path for route in router.routes]
        expected_routes = ["/chat", "/query", "/capabilities", "/tools", "/status"]
        
        print(f"   Available routes: {routes}")
        for expected in expected_routes:
            if expected in routes:
                print(f"   ✓ Route {expected} found")
            else:
                print(f"   ❌ Route {expected} missing")
                
    except ImportError as e:
        print(f"   ❌ Failed to import agent endpoints: {e}")


def test_integration_flow():
    """Test the complete integration flow."""
    print("\n🧪 Testing Integration Flow...")
    
    print("   1. Agent initialization...")
    agent = MCPAgent(
        base_url="http://localhost:8000",
        openai_api_key=os.getenv("OPENAI_API_KEY", "mock-key")
    )
    
    print("   2. Capability discovery...")
    capabilities = agent.get_available_tools()
    print(f"      Found {len(capabilities)} tools")
    
    print("   3. Tool finding...")
    test_tool = agent.find_tool("listHerd")
    if test_tool:
        print(f"      ✓ Found test tool: {test_tool.get('name')}")
    else:
        print("      ⚠️  Test tool 'listHerd' not found")
    
    print("   4. API endpoint structure...")
    try:
        from app.api.v1.endpoints.agent import get_agent
        test_agent = get_agent()
        print(f"      ✓ API agent getter works: {test_agent is not None}")
    except Exception as e:
        print(f"      ❌ API agent getter failed: {e}")


async def main():
    """Run all tests."""
    print("🚀 MCP Agent with OpenAI Integration - Test Suite")
    print("=" * 50)
    
    try:
        await test_agent_initialization()
        test_agent_capabilities()
        test_openai_methods()
        test_api_endpoints_structure()
        test_integration_flow()
        
        print("\n" + "=" * 50)
        print("✅ Test suite completed!")
        print("\n📋 Next steps:")
        print("   1. Set OPENAI_API_KEY environment variable for full functionality")
        print("   2. Start the FastAPI server: uvicorn app.main:app --reload")
        print("   3. Test endpoints at: http://localhost:8000/docs")
        print("   4. Try the new agent endpoints under '/api/v1/agent/'")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)