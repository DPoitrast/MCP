import textwrap
import pytest

from agent.mcp_agent import MCPAgent


def test_list_herd_missing_path(tmp_path):
    context_file = tmp_path / "context.yaml"
    context_file.write_text(
        textwrap.dedent(
            """
            api:
              version: v1
              tools:
                - name: listHerd
                  method: GET
            """
        )
    )

    agent = MCPAgent("http://example.com", context_path=str(context_file))
    with pytest.raises(ValueError, match="listHerd tool path not found"):
        agent.list_herd("token")

