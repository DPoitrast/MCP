import textwrap
import pytest
import json
from unittest import mock
import requests  # For requests.exceptions

from agent.mcp_agent import MCPAgent


# Keep existing test
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


class TestParseContextFallback:
    def test_parse_fallback_minimal_version_only(self, tmp_path):
        context_file = tmp_path / "context.yaml"
        context_file.write_text("api:\n  version: v1alpha\n")
        context = MCPAgent._parse_context_fallback(str(context_file))
        assert context == {"api": {"version": "v1alpha", "tools": []}}

    def test_parse_fallback_single_tool(self, tmp_path):
        context_file = tmp_path / "context.yaml"
        content = textwrap.dedent(
            """
            api:
              version: v1
              tools:
                - name: listHerd
                  method: GET
                  path: /herd
            """
        )
        context_file.write_text(content)
        context = MCPAgent._parse_context_fallback(str(context_file))
        expected = {
            "api": {
                "version": "v1",
                "tools": [{"name": "listHerd", "method": "GET", "path": "/herd"}],
            }
        }
        assert context == expected

    def test_parse_fallback_multiple_tools(self, tmp_path):
        context_file = tmp_path / "context.yaml"
        content = textwrap.dedent(
            """
            api:
              version: v1
              tools:
                - name: listHerd
                  method: GET
                  path: /herd
                - name: getSheep
                  method: GET
                  path: /sheep/{id}
            """
        )
        context_file.write_text(content)
        context = MCPAgent._parse_context_fallback(str(context_file))
        expected = {
            "api": {
                "version": "v1",
                "tools": [
                    {"name": "listHerd", "method": "GET", "path": "/herd"},
                    {"name": "getSheep", "method": "GET", "path": "/sheep/{id}"},
                ],
            }
        }
        assert context == expected

    def test_parse_fallback_malformed_content_skips_unknown_lines(self, tmp_path):
        context_file = tmp_path / "context.yaml"
        content = textwrap.dedent(
            """
            api:
              version: v1
              tools:
                - name: toolOne
                  method: GET
                  unexpected_line: should be skipped
                  path: /pathOne
                - name: toolTwo
                  invalid_property_before_method: true
                  method: POST
                  path: /pathTwo
            """
        )
        # Fallback parser is very basic, it only looks for specific prefixes.
        # Lines that don't match known prefixes are ignored.
        # Properties like 'method' or 'path' are associated with the most recent 'name'.
        context_file.write_text(content)
        context = MCPAgent._parse_context_fallback(str(context_file))
        expected = {
            "api": {
                "version": "v1",
                "tools": [
                    {"name": "toolOne", "method": "GET", "path": "/pathOne"},
                    {"name": "toolTwo", "method": "POST", "path": "/pathTwo"},
                ],
            }
        }
        assert context == expected

    def test_parse_fallback_tool_with_name_only(self, tmp_path):
        context_file = tmp_path / "context.yaml"
        content = textwrap.dedent(
            """
            api:
              version: v1
              tools:
                - name: listHerd
                  # Method and path are missing
            """
        )
        context_file.write_text(content)
        context = MCPAgent._parse_context_fallback(str(context_file))
        expected = {"api": {"version": "v1", "tools": [{"name": "listHerd"}]}}
        assert context == expected

    def test_parse_fallback_empty_file(self, tmp_path):
        context_file = tmp_path / "context.yaml"
        context_file.write_text("")  # Empty file
        context = MCPAgent._parse_context_fallback(str(context_file))
        assert context == {"api": {"tools": []}}  # Default context

    def test_parse_fallback_file_not_found(self):
        # Test _parse_context_fallback directly for non-existent file
        context = MCPAgent._parse_context_fallback("non_existent_dummy_file.yaml")
        assert context == {"api": {"tools": []}}


def test_parse_context_constructor_file_not_found():
    # This test instantiates MCPAgent, which calls _parse_context.
    # _parse_context will use PyYAML if available, or _parse_context_fallback otherwise.
    # Both should handle FileNotFoundError by returning the default context.
    agent = MCPAgent(
        "http://example.com", context_path="non_existent_file_for_sure.yaml"
    )
    assert agent.context == {"api": {"tools": []}}


class TestListHerd:
    @pytest.fixture
    def valid_agent(self, tmp_path):
        context_file = tmp_path / "context.yaml"
        content = textwrap.dedent(
            """
            api:
              version: v1
              tools:
                - name: listHerd
                  method: GET
                  path: /test/herd
            """
        )
        context_file.write_text(content)
        return MCPAgent("http://fakeapi.com", context_path=str(context_file))

    @mock.patch("agent.mcp_agent.requests.get")
    def test_list_herd_success(self, mock_get, valid_agent):
        mock_response = mock.Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "Sheepie"}]
        # mock_response.raise_for_status() will do nothing if status_code < 400

        mock_get.return_value = mock_response

        result = valid_agent.list_herd("test_token_123")

        assert result == [{"id": 1, "name": "Sheepie"}]
        mock_get.assert_called_once_with(
            "http://fakeapi.com/test/herd",
            headers={"Authorization": "Bearer test_token_123"},
        )
        mock_response.raise_for_status.assert_called_once()

    @mock.patch("agent.mcp_agent.requests.get")
    def test_list_herd_http_error(self, mock_get, valid_agent):
        mock_response = mock.Mock(spec=requests.Response)
        mock_response.status_code = 503
        mock_response.reason = "Service Unavailable"

        # Configure raise_for_status to raise HTTPError
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error

        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="HTTP error 503: Service Unavailable"):
            valid_agent.list_herd("test_token_456")

        mock_get.assert_called_once_with(
            "http://fakeapi.com/test/herd",
            headers={"Authorization": "Bearer test_token_456"},
        )
        mock_response.raise_for_status.assert_called_once()

    @mock.patch("agent.mcp_agent.requests.get")
    def test_list_herd_request_exception(self, mock_get, valid_agent):
        # Test for general requests.exceptions.RequestException (e.g., connection error)
        connection_error_msg = "Failed to establish a new connection"
        mock_get.side_effect = requests.exceptions.ConnectionError(connection_error_msg)

        with pytest.raises(
            RuntimeError, match=f"Request error: {connection_error_msg}"
        ):
            valid_agent.list_herd("test_token_789")

        mock_get.assert_called_once_with(
            "http://fakeapi.com/test/herd",
            headers={"Authorization": "Bearer test_token_789"},
        )

    def test_list_herd_tool_not_in_context(self, tmp_path):
        context_file = tmp_path / "context.yaml"
        # Context definition without the 'listHerd' tool
        context_file.write_text(
            textwrap.dedent(
                """
                api:
                  version: v1
                  tools:
                    - name: anotherTool
                      method: GET
                      path: /another
                """
            )
        )
        agent_no_listherd = MCPAgent(
            "http://example.com", context_path=str(context_file)
        )
        with pytest.raises(
            ValueError, match="listHerd tool not found in model context"
        ):
            agent_no_listherd.list_herd("a_token")
