from .mcp_agent import MCPAgent
import argparse


def main():
    parser = argparse.ArgumentParser(description="Interact with MCP server")
    parser.add_argument(
        "base_url", help="Base URL of the MCP server, e.g. http://localhost:8000"
    )
    parser.add_argument(
        "--token", default="fake-super-secret-token", help="Bearer token"
    )
    args = parser.parse_args()

    agent = MCPAgent(args.base_url)
    data = agent.list_herd(args.token)
    print(data)


if __name__ == "__main__":
    main()
