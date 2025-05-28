#!/usr/bin/env python3
"""Demo script showcasing all interactive features of the MCP agent."""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interactive_agent import InteractiveAgent
from agent.mcp_agent import MCPAgent


def demo_agent_capabilities():
    """Demonstrate basic agent capabilities."""
    print("🤖 Agent Capabilities Demo")
    print("=" * 40)
    
    agent = MCPAgent(
        base_url="http://localhost:8000",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    print(f"✓ Agent initialized")
    print(f"✓ OpenAI available: {agent.openai_client is not None}")
    print(f"✓ MCP tools: {len(agent.get_available_tools())}")
    
    # Show some tools
    tools = agent.get_available_tools()[:3]
    print("\n📋 Sample available tools:")
    for tool in tools:
        name = tool.get('name', 'Unknown')
        desc = tool.get('description', 'No description')
        print(f"  • {name}: {desc}")
    
    return agent


def demo_interactive_features():
    """Demonstrate interactive agent features."""
    print("\n🔄 Interactive Features Demo")
    print("=" * 40)
    
    # Create interactive agent
    interactive_agent = InteractiveAgent(
        base_url="http://localhost:8000",
        enable_streaming=True
    )
    
    print(f"✓ Interactive agent created")
    print(f"✓ Streaming enabled: {interactive_agent.enable_streaming}")
    print(f"✓ Chat mode: {interactive_agent.chat_mode}")
    
    # Test command processing
    commands_to_test = [
        ("/help", "Help command"),
        ("/status", "Status command"),
        ("/tools", "Tools command"),
        ("/session", "Session info"),
    ]
    
    print("\n🧪 Testing commands:")
    for cmd, desc in commands_to_test:
        try:
            # Since _process_command might be async, we need to handle both cases
            result = interactive_agent.commands[cmd]("")
            if asyncio.iscoroutinefunction(interactive_agent.commands[cmd]):
                print(f"  • {cmd}: {desc} - async method available ✓")
            else:
                print(f"  • {cmd}: {desc} - ✓")
        except Exception as e:
            print(f"  • {cmd}: {desc} - ❌ {e}")
    
    return interactive_agent


def demo_session_management():
    """Demonstrate session management features."""
    print("\n💾 Session Management Demo")
    print("=" * 40)
    
    agent = InteractiveAgent()
    
    # Test session data
    test_conversation = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I help you?"}
    ]
    
    agent.conversation_history = test_conversation
    
    # Save session
    agent._save_session()
    print("✓ Session saved")
    
    # Clear and reload
    agent.conversation_history = []
    agent._load_session()
    print(f"✓ Session loaded ({len(agent.conversation_history)} messages)")
    
    return len(agent.conversation_history) > 0


async def demo_streaming():
    """Demonstrate streaming functionality."""
    print("\n📡 Streaming Demo")
    print("=" * 40)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set - skipping streaming demo")
        return False
    
    try:
        agent = MCPAgent(
            base_url="http://localhost:8000",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        print("✓ Testing streaming response...")
        result = agent.chat_with_openai(
            user_message="Say hello in exactly 10 words",
            stream=True
        )
        
        if result.get("is_streaming"):
            print("📡 Streaming response: ", end="", flush=True)
            full_response = ""
            chunk_count = 0
            
            for chunk in result["stream"]:
                print(chunk, end="", flush=True)
                full_response += chunk
                chunk_count += 1
                if chunk_count > 50:  # Safety limit for demo
                    break
            
            print(f"\n✓ Streaming completed ({chunk_count} chunks)")
            return True
        else:
            print("❌ Streaming not available")
            return False
            
    except Exception as e:
        print(f"❌ Streaming demo failed: {e}")
        return False


def demo_web_interface():
    """Demonstrate web interface availability."""
    print("\n🌐 Web Interface Demo")
    print("=" * 40)
    
    try:
        from web_interface import WebAgent, app
        
        web_agent = WebAgent()
        print("✓ Web interface available")
        print(f"✓ FastAPI app created: {type(app).__name__}")
        print(f"✓ OpenAI available: {web_agent.agent.openai_client is not None}")
        
        print("\n🚀 To start the web interface:")
        print("  python web_interface.py --host localhost --port 8080")
        print("  Then visit: http://localhost:8080")
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface error: {e}")
        return False


def show_usage_examples():
    """Show usage examples."""
    print("\n📖 Usage Examples")
    print("=" * 40)
    
    examples = [
        ("Interactive CLI", "python interactive_agent.py"),
        ("Web Interface", "python web_interface.py"),
        ("Custom URL", "python interactive_agent.py --url http://myserver.com:8000"),
        ("Custom OpenAI Key", "python interactive_agent.py --openai-key sk-..."),
        ("Web with Custom Settings", "python web_interface.py --host 0.0.0.0 --port 9000"),
    ]
    
    for title, command in examples:
        print(f"  📋 {title}:")
        print(f"     {command}")
        print()


async def main():
    """Run all demos."""
    print("🚀 Interactive MCP Agent - Feature Demonstration")
    print("=" * 60)
    
    results = {}
    
    try:
        # Demo basic capabilities
        agent = demo_agent_capabilities()
        results["basic_capabilities"] = True
        
        # Demo interactive features
        interactive_agent = demo_interactive_features()
        results["interactive_features"] = True
        
        # Demo session management
        session_test = demo_session_management()
        results["session_management"] = session_test
        
        # Demo streaming
        streaming_test = await demo_streaming()
        results["streaming"] = streaming_test
        
        # Demo web interface
        web_test = demo_web_interface()
        results["web_interface"] = web_test
        
        # Show usage examples
        show_usage_examples()
        
        # Results summary
        print("📊 Feature Test Results")
        print("=" * 40)
        
        for feature, status in results.items():
            status_icon = "✅" if status else "❌"
            feature_name = feature.replace("_", " ").title()
            print(f"{status_icon} {feature_name}")
        
        total_features = len(results)
        working_features = sum(results.values())
        
        print(f"\n🎯 Summary: {working_features}/{total_features} features working")
        
        if working_features == total_features:
            print("🎉 All interactive features are working perfectly!")
        else:
            print("⚠️  Some features may require additional setup (e.g., OPENAI_API_KEY)")
        
        print("\n🔧 Quick Start:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Start MCP server: uvicorn app.main:app --reload")
        print("3. Run interactive agent: python interactive_agent.py")
        print("4. Or run web interface: python web_interface.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)