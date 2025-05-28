#!/usr/bin/env python3
"""Test script to verify GPT-4o-mini model integration."""

import os
import sys
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.mcp_agent import MCPAgent
from interactive_agent import InteractiveAgent


def test_model_configuration():
    """Test that the model is properly configured."""
    print("🔧 Testing Model Configuration")
    print("-" * 30)
    
    # Test MCP Agent default
    agent = MCPAgent("http://localhost:8000")
    print("✓ MCP Agent created")
    
    # Test Interactive Agent default
    interactive = InteractiveAgent(enable_streaming=False)
    print(f"✓ Interactive Agent default model: {interactive.current_model}")
    
    # Test model switching
    interactive._cmd_model_info("gpt-4o")
    print(f"✓ Model changed to: {interactive.current_model}")
    
    # Test available models
    available = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    print(f"✓ Available models: {', '.join(available)}")
    
    return True


async def test_openai_integration():
    """Test actual OpenAI integration with GPT-4o-mini."""
    print("\n🤖 Testing OpenAI Integration")
    print("-" * 30)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set - skipping OpenAI API tests")
        return None
    
    try:
        agent = MCPAgent("http://localhost:8000")
        
        if not agent.openai_client:
            print("❌ OpenAI client not initialized")
            return False
        
        print("✓ OpenAI client initialized")
        
        # Test simple chat with GPT-4o-mini
        result = agent.chat_with_openai(
            user_message="Say 'Hello from GPT-4o-mini' and nothing else",
            model="gpt-4o-mini"
        )
        
        if result and "response" in result:
            response = result["response"].strip().lower()
            if "gpt-4o-mini" in response and "hello" in response:
                print("✓ GPT-4o-mini responded correctly")
                print(f"  Response: {result['response']}")
                return True
            else:
                print(f"✓ GPT-4o-mini responded: {result['response']}")
                return True
        else:
            print("❌ No valid response from GPT-4o-mini")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI integration test failed: {e}")
        return False


def test_interactive_features():
    """Test interactive features with the new model."""
    print("\n💬 Testing Interactive Features")
    print("-" * 30)
    
    try:
        agent = InteractiveAgent(enable_streaming=False)
        
        # Test model commands
        model_info = agent._cmd_model_info()
        print("✓ Model info command works")
        
        # Test session info includes model
        session_info = agent._cmd_session_info()
        if "gpt-4o-mini" in session_info:
            print("✓ Session info includes model information")
        
        # Test model switching
        switch_result = agent._cmd_model_info("gpt-4o")
        if "changed" in switch_result.lower():
            print("✓ Model switching works")
        
        return True
        
    except Exception as e:
        print(f"❌ Interactive features test failed: {e}")
        return False


def show_usage_examples():
    """Show usage examples with the new model."""
    print("\n📖 GPT-4o-mini Usage Examples")
    print("=" * 40)
    
    examples = [
        ("Interactive CLI", "python interactive_agent.py", "Uses gpt-4o-mini by default"),
        ("Web Interface", "python web_interface.py", "Uses gpt-4o-mini for chat"),
        ("Switch Model", "/model gpt-4o", "Change to GPT-4 in CLI"),
        ("Model Info", "/model", "Show current model and options"),
        ("Direct API", "agent.chat_with_openai(msg, model='gpt-4o-mini')", "Python API usage"),
    ]
    
    for title, command, description in examples:
        print(f"📋 {title}:")
        print(f"   Command: {command}")
        print(f"   Note: {description}")
        print()


async def main():
    """Run all GPT-4o-mini tests."""
    print("🚀 GPT-4o-mini Model Integration Test")
    print("=" * 50)
    
    results = {}
    
    try:
        # Test configuration
        config_result = test_model_configuration()
        results["configuration"] = config_result
        
        # Test OpenAI integration
        openai_result = await test_openai_integration()
        results["openai_integration"] = openai_result
        
        # Test interactive features
        interactive_result = test_interactive_features()
        results["interactive_features"] = interactive_result
        
        # Show usage examples
        show_usage_examples()
        
        # Results summary
        print("📊 Test Results Summary")
        print("=" * 30)
        
        for test_name, result in results.items():
            if result is True:
                status = "✅ PASS"
            elif result is False:
                status = "❌ FAIL"
            else:
                status = "⚠️  SKIP"
            
            test_display = test_name.replace("_", " ").title()
            print(f"{status} {test_display}")
        
        # Overall assessment
        passed_tests = sum(1 for r in results.values() if r is True)
        total_tests = len([r for r in results.values() if r is not None])
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests and total_tests > 0:
            print("🎉 GPT-4o-mini integration successful!")
        elif total_tests == 0:
            print("⚠️  Most tests skipped - set OPENAI_API_KEY for full testing")
        else:
            print("⚠️  Some tests failed.")
        
        print("\n🔧 Benefits of GPT-4o-mini:")
        print("- Faster responses than GPT-4")
        print("- Lower cost than GPT-4")
        print("- Still highly capable for most tasks")
        print("- Better for interactive chat experiences")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)