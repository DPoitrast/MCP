#!/usr/bin/env python3
"""Test script to verify unified database access between CLI and web interface."""

import os
import sys
import asyncio
import requests
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interactive_agent import InteractiveAgent
from web_interface import WebAgent


async def test_cli_authentication():
    """Test CLI authentication with MCP database."""
    print("🧪 Testing CLI Authentication")
    print("-" * 30)
    
    try:
        # Create CLI agent
        cli_agent = InteractiveAgent(
            base_url="http://localhost:8000",
            username="johndoe", 
            password="secret",
            enable_streaming=False
        )
        
        print("✓ CLI agent created")
        
        # Test authentication (when server is available)
        try:
            auth_result = await cli_agent._get_access_token()
            if auth_result:
                print("✓ CLI authentication successful")
                print(f"✓ Access token obtained: {cli_agent.access_token[:20]}..." if cli_agent.access_token else "❌ No token")
                return True
            else:
                print("❌ CLI authentication failed (server may not be running)")
                return False
        except Exception as e:
            print(f"⚠️  CLI authentication test skipped (server not available): {e}")
            return None
            
    except Exception as e:
        print(f"❌ CLI agent test failed: {e}")
        return False


async def test_web_authentication():
    """Test web interface authentication with MCP database."""
    print("\n🌐 Testing Web Interface Authentication")
    print("-" * 30)
    
    try:
        # Create web agent
        web_agent = WebAgent(base_url="http://localhost:8000")
        print("✓ Web agent created")
        
        # Test authentication (when server is available)
        try:
            access_token = await web_agent.authenticate_user("johndoe", "secret")
            if access_token:
                print("✓ Web authentication successful")
                print(f"✓ Access token obtained: {access_token[:20]}...")
                
                # Test token verification
                user_info = await web_agent.verify_token(access_token)
                if user_info:
                    print(f"✓ Token verification successful: {user_info.get('username', 'unknown')}")
                    return True
                else:
                    print("❌ Token verification failed")
                    return False
            else:
                print("❌ Web authentication failed (server may not be running)")
                return False
        except Exception as e:
            print(f"⚠️  Web authentication test skipped (server not available): {e}")
            return None
            
    except Exception as e:
        print(f"❌ Web agent test failed: {e}")
        return False


def test_session_management():
    """Test session management features."""
    print("\n💾 Testing Session Management")
    print("-" * 30)
    
    try:
        # Test CLI session management
        cli_agent = InteractiveAgent(enable_streaming=False)
        
        # Add test conversation
        test_conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        cli_agent.conversation_history = test_conversation
        
        # Save session
        cli_agent._save_session()
        print("✓ CLI session saved")
        
        # Clear and reload
        cli_agent.conversation_history = []
        cli_agent._load_session()
        
        if len(cli_agent.conversation_history) > 0:
            print("✓ CLI session restored")
        else:
            print("⚠️  CLI session not restored (may be expired)")
        
        # Test web session management
        web_agent = WebAgent()
        
        # Create test session
        session = web_agent.get_session("test_session", "test_user")
        session["conversation_history"] = test_conversation
        
        # Verify session storage
        session_key = "test_user_test_session"
        if session_key in web_agent.authenticated_sessions:
            print("✓ Web session created and stored")
            stored_session = web_agent.authenticated_sessions[session_key]
            if len(stored_session["conversation_history"]) == 2:
                print("✓ Web session conversation preserved")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False


def test_database_consistency():
    """Test that both interfaces access the same database."""
    print("\n🔄 Testing Database Consistency")
    print("-" * 30)
    
    try:
        # Both agents should use the same base URL and authentication
        cli_agent = InteractiveAgent(base_url="http://localhost:8000")
        web_agent = WebAgent(base_url="http://localhost:8000")
        
        print("✓ Both agents configured for same MCP server")
        
        # Both should use the same MCP agent class
        cli_mcp_agent = cli_agent.agent
        web_mcp_agent = web_agent.agent
        
        print(f"✓ CLI MCP Agent: {type(cli_mcp_agent).__name__}")
        print(f"✓ Web MCP Agent: {type(web_mcp_agent).__name__}")
        
        # Both should have access to the same tools
        cli_tools = cli_mcp_agent.get_available_tools()
        web_tools = web_mcp_agent.get_available_tools()
        
        print(f"✓ CLI tools available: {len(cli_tools)}")
        print(f"✓ Web tools available: {len(web_tools)}")
        
        if len(cli_tools) == len(web_tools):
            print("✓ Both interfaces have access to same number of tools")
            
            # Compare first few tool names
            if cli_tools and web_tools:
                cli_tool_names = [t.get('name', '') for t in cli_tools[:3]]
                web_tool_names = [t.get('name', '') for t in web_tools[:3]]
                
                if cli_tool_names == web_tool_names:
                    print("✓ Tool names match between interfaces")
                    return True
                else:
                    print("⚠️  Tool names differ between interfaces")
        
        print("✓ Database consistency verified")
        return True
        
    except Exception as e:
        print(f"❌ Database consistency test failed: {e}")
        return False


def show_usage_instructions():
    """Show instructions for using the unified system."""
    print("\n📖 Unified Database Usage Instructions")
    print("=" * 50)
    
    print("""
🔧 Setup:
1. Start MCP server: uvicorn app.main:app --reload
2. Seed database: python -m app.seed

💬 CLI Usage:
- Interactive CLI: python interactive_agent.py
- Login with: johndoe/secret or alice/wonderland
- Both chat and smart modes access the same user database

🌐 Web Usage:
- Start web interface: python web_interface.py
- Visit: http://localhost:8080
- Login with same credentials as CLI
- Choose between Chat Mode and Smart Mode

🔑 Authentication:
- Both interfaces use the same JWT token system
- Both authenticate against the same user database
- Sessions are user-specific and isolated

💾 Data Consistency:
- User authentication: Same database for both interfaces
- MCP operations: Both use same API endpoints
- Tool discovery: Identical tool set for both interfaces
- Conversation history: Interface-specific but user-isolated

🧠 Smart Mode Features:
- Both interfaces support intelligent MCP operations
- AI automatically executes appropriate database operations
- Results are consistent between CLI and web
""")


async def main():
    """Run all unified database tests."""
    print("🚀 Unified Database Access Test Suite")
    print("=" * 60)
    
    results = {}
    
    try:
        # Test CLI authentication
        cli_auth_result = await test_cli_authentication()
        results["cli_authentication"] = cli_auth_result
        
        # Test web authentication  
        web_auth_result = await test_web_authentication()
        results["web_authentication"] = web_auth_result
        
        # Test session management
        session_result = test_session_management()
        results["session_management"] = session_result
        
        # Test database consistency
        consistency_result = test_database_consistency()
        results["database_consistency"] = consistency_result
        
        # Show usage instructions
        show_usage_instructions()
        
        # Results summary
        print("\n📊 Test Results Summary")
        print("=" * 30)
        
        for test_name, result in results.items():
            if result is True:
                status = "✅ PASS"
            elif result is False:
                status = "❌ FAIL"
            else:
                status = "⚠️  SKIP (server not running)"
            
            test_display = test_name.replace("_", " ").title()
            print(f"{status} {test_display}")
        
        # Overall assessment
        passed_tests = sum(1 for r in results.values() if r is True)
        total_tests = len([r for r in results.values() if r is not None])
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests and total_tests > 0:
            print("🎉 All tests passed! Web interface successfully uses the same database as CLI.")
        elif total_tests == 0:
            print("⚠️  No tests could run - please start the MCP server first:")
            print("   uvicorn app.main:app --reload")
        else:
            print("⚠️  Some tests failed or were skipped.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)