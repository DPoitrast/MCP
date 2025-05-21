from agent.mcp_agent import MCPAgent

EXPECTED_CONTEXT = {
    "schema_version": 1,
    "api": {
        "version": "v1",
        "tools": [
            {
                "name": "listHerd",
                "method": "GET",
                "path": "/api/v1/herd",
                "description": "Retrieve herd information",
                "scopes": ["herd.read"],
            }
        ],
    },
}


def test_parse_context(tmp_path):
    # Copy model_context.yaml to temporary directory to avoid modifying original
    src_path = "model_context.yaml"
    dest = tmp_path / "ctx.yaml"
    with open(src_path, "r", encoding="utf-8") as f_src:
        dest.write_text(f_src.read(), encoding="utf-8")

    agent = MCPAgent("http://localhost", context_path=str(dest))
    assert agent.context == EXPECTED_CONTEXT
