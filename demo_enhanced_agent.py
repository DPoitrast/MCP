#!/usr/bin/env python3
"""
Demonstration of the Enhanced MCP Agent with Dynamic Discovery

This script showcases the sophisticated MCP agent capabilities:
1. Dynamic API discovery through OpenAPI metadata
2. Automatic tool generation and execution
3. Fallback to static configuration
4. Comprehensive operation support
"""

import json
import time
import uvicorn
import multiprocessing
from app.main import app
from agent.mcp_agent import MCPAgent


def run_server():
    """Run the MCP server in background."""
    uvicorn.run(app, host='127.0.0.1', port=8003, log_level='error')


def demo_enhanced_agent():
    """Demonstrate the enhanced MCP agent capabilities."""
    print("🚀 Enhanced MCP Agent Demonstration")
    print("=" * 60)
    
    # Start server
    print("📡 Starting MCP server...")
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    time.sleep(3)  # Give server time to start
    
    try:
        print("\n1️⃣ Dynamic Discovery vs Static Configuration")
        print("-" * 50)
        
        # Test dynamic discovery
        print("🔍 Creating agent with dynamic discovery...")
        dynamic_agent = MCPAgent('http://localhost:8003', auto_discover=True)
        dynamic_tools = dynamic_agent.get_available_tools()
        print(f"✓ Dynamically discovered {len(dynamic_tools)} tools")
        
        # Test static configuration  
        print("📄 Creating agent with static configuration...")
        static_agent = MCPAgent('http://localhost:8003', auto_discover=False)
        static_tools = static_agent.get_available_tools()
        print(f"✓ Loaded {len(static_tools)} tools from static config")
        
        print(f"\n📊 Discovery Results:")
        print(f"   Dynamic: {len(dynamic_tools)} tools")
        print(f"   Static:  {len(static_tools)} tools")
        print(f"   Ratio:   {len(dynamic_tools)/len(static_tools):.1f}x more with dynamic discovery")
        
        print("\n2️⃣ Available Operations")
        print("-" * 50)
        
        # Group tools by category
        categories = {}
        for tool in dynamic_tools:
            tags = tool.get('tags', ['general'])
            category = tags[0] if tags else 'general'
            if category not in categories:
                categories[category] = []
            categories[category].append(tool)
        
        for category, tools in categories.items():
            print(f"\n📁 {category.upper()} ({len(tools)} operations):")
            for tool in tools:
                method = tool.get('method', 'unknown')
                path = tool.get('path', 'unknown')
                desc = tool.get('description', 'No description')
                print(f"   🔧 {method:6} {path:35} - {desc}")
        
        print("\n3️⃣ Operation Execution Examples")
        print("-" * 50)
        
        token = "fake-super-secret-token"
        
        # Health check
        print("🏥 Health Check:")
        health = dynamic_agent.execute_operation('health_check_api_v1_health_get', token)
        print(f"   Status: {health['status']}")
        print(f"   Database: {health['database']}")
        print(f"   Version: {health['version']}")
        
        # List herds
        print("\n🐄 List Herds:")
        herds_result = dynamic_agent.execute_operation('list_herds_api_v1_herd_get', token, limit=3)
        print(f"   Total herds: {herds_result['total']}")
        print(f"   Showing {len(herds_result['items'])} items:")
        for herd in herds_result['items']:
            print(f"     • {herd['name']} in {herd['location']}")
        
        # Statistics
        print("\n📊 Statistics:")
        stats = dynamic_agent.execute_operation('get_herd_statistics_api_v1_herd_stats_get', token)
        print(f"   Total herds: {stats['total_herds']}")
        print(f"   Max query limit: {stats['max_query_limit']}")
        
        # Search
        print("\n🔍 Search by Name:")
        search_results = dynamic_agent.execute_operation(
            'search_herds_by_name_api_v1_herd_search_name_get', 
            token, 
            name='Alpha'
        )
        print(f"   Found {len(search_results)} herds matching 'Alpha':")
        for herd in search_results:
            print(f"     • {herd['name']} in {herd['location']}")
        
        # Create new herd
        print("\n➕ Create New Herd:")
        new_herd = dynamic_agent.execute_operation(
            'create_herd_api_v1_herd_post', 
            token,
            name='Demo Farm',
            location='Virtual Valley'
        )
        print(f"   Created: {new_herd['name']} (ID: {new_herd['id']})")
        
        # Get specific herd
        print(f"\n🎯 Get Specific Herd (ID: {new_herd['id']}):")
        specific_herd = dynamic_agent.execute_operation(
            'get_herd_api_v1_herd__herd_id__get',
            token,
            herd_id=new_herd['id']
        )
        print(f"   Retrieved: {specific_herd['name']} in {specific_herd['location']}")
        
        # Update herd
        print(f"\n✏️ Update Herd (ID: {new_herd['id']}):")
        updated_herd = dynamic_agent.execute_operation(
            'update_herd_api_v1_herd__herd_id__put',
            token,
            herd_id=new_herd['id'],
            location='Updated Virtual Valley'
        )
        print(f"   Updated location: {updated_herd['location']}")
        
        print("\n4️⃣ Error Handling & Fallback")
        print("-" * 50)
        
        # Test with invalid server (should fallback to static config)
        print("🔧 Testing fallback to static configuration...")
        fallback_agent = MCPAgent('http://localhost:9999', auto_discover=True)  # Invalid port
        fallback_tools = fallback_agent.get_available_tools()
        print(f"✓ Gracefully fell back to static config ({len(fallback_tools)} tools)")
        
        print("\n5️⃣ Dynamic vs Static Comparison")
        print("-" * 50)
        
        print("📈 Capabilities comparison:")
        print(f"   Dynamic Discovery:")
        print(f"     • Auto-detects all API endpoints")
        print(f"     • No manual configuration needed")
        print(f"     • Always up-to-date with server changes")
        print(f"     • Provides parameter information")
        print(f"     • Supports all HTTP methods")
        print(f"   Static Configuration:")
        print(f"     • Requires manual YAML updates")
        print(f"     • May become outdated")
        print(f"     • Limited to predefined operations")
        print(f"     • Simpler, more predictable")
        print(f"     • Works offline")
        
        print("\n✅ Enhanced MCP Agent Demonstration Complete!")
        print(f"🎉 Successfully demonstrated {len(dynamic_tools)} dynamically discovered operations")
        
    finally:
        # Clean up
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.join()


if __name__ == "__main__":
    demo_enhanced_agent()