from .mcp_agent import MCPAgent
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Sophisticated MCP Agent with Dynamic Discovery")
    parser.add_argument(
        "base_url", help="Base URL of the MCP server, e.g. http://localhost:8000"
    )
    parser.add_argument(
        "--token", default="fake-super-secret-token", help="Bearer token"
    )
    parser.add_argument(
        "--no-discover", action="store_true", 
        help="Disable dynamic discovery, use static context only"
    )
    parser.add_argument(
        "--list-tools", action="store_true",
        help="List all available tools/operations"
    )
    parser.add_argument(
        "--execute", metavar="TOOL_NAME",
        help="Execute a specific tool by name"
    )
    parser.add_argument(
        "--params", type=str,
        help="JSON string of parameters for tool execution, e.g. '{\"skip\": 0, \"limit\": 10}'"
    )
    args = parser.parse_args()

    # Create agent with dynamic discovery
    try:
        agent = MCPAgent(args.base_url, auto_discover=not args.no_discover)
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)

    # List available tools
    if args.list_tools:
        tools = agent.get_available_tools()
        print(f"\n📋 Available Tools ({len(tools)} total):")
        print("=" * 60)
        for tool in tools:
            print(f"🔧 {tool.get('name', 'unnamed')}")
            print(f"   Method: {tool.get('method', 'unknown')}")
            print(f"   Path: {tool.get('path', 'unknown')}")
            print(f"   Description: {tool.get('description', 'No description')}")
            if tool.get('parameters'):
                print(f"   Parameters: {len(tool['parameters'])} defined")
            print()
        return

    # Execute specific tool
    if args.execute:
        try:
            params = {}
            if args.params:
                params = json.loads(args.params)
            
            result = agent.execute_operation(args.execute, args.token, **params)
            print(f"✅ Executed '{args.execute}' successfully:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Failed to execute '{args.execute}': {e}")
            sys.exit(1)
        return

    # Default behavior: list herds using the original method for backward compatibility
    try:
        if hasattr(agent, 'capabilities') and agent.capabilities:
            # Use dynamic discovery
            result = agent.execute_operation("list_herd", args.token)
        else:
            # Fallback to static method
            result = agent.list_herd(args.token)
        
        print("🐄 Herds:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Failed to list herds: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
