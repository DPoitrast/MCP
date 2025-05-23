try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


class MCPAgent:
    """Simple agent for interacting with the MCP API."""

    def __init__(self, base_url: str, context_path: str = "model_context.yaml"):
        self.base_url = base_url.rstrip('/')
        self.context = self._parse_context(context_path)

    @staticmethod
    def _parse_context(path: str) -> dict:
        """Parse the model context YAML file."""
        if yaml is not None:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                if not isinstance(data, dict):
                    raise ValueError("Model context must be a mapping")
                return data
            except FileNotFoundError:
                return {"api": {"tools": []}}
            except yaml.YAMLError as exc:  # pragma: no cover - difficult to trigger
                raise ValueError(f"Error parsing {path}: {exc}") from exc
        # PyYAML not available, use fallback parser
        return MCPAgent._parse_context_fallback(path)

    @staticmethod
    def _parse_context_fallback(path: str) -> dict:
        """Parse the model context YAML file using a fallback parser."""
        context = {"api": {"tools": []}}
        try:
            with open(path, "r", encoding="utf-8") as f:
                tool = None
                for raw_line in f:
                    line = raw_line.strip()
                    if line.startswith("version:"):
                        context.setdefault("api", {})["version"] = line.split(":", 1)[1].strip()
                    elif line.startswith("- name:"):
                        name = line.split(":", 1)[1].strip()
                        tool = {"name": name}
                        context["api"]["tools"].append(tool)
                    elif line.startswith("method:") and tool is not None:
                        tool["method"] = line.split(":", 1)[1].strip()
                    elif line.startswith("path:") and tool is not None:
                        tool["path"] = line.split(":", 1)[1].strip()
        except FileNotFoundError:
            # If the file is not found, return the default context,
            # which is an empty list of tools. This matches the behavior
            # of the original PyYAML based parser.
            pass
        return context

    def list_herd(self, token: str) -> list:
        """Call the listHerd endpoint and return JSON data."""
        tool = next(
            (
                t
                for t in self.context.get("api", {}).get("tools", [])
                if t.get("name") == "listHerd"
            ),
            None,
        )
        if tool is None:
            raise ValueError("listHerd tool not found in model context")
        path = tool.get("path")
        if not path:
            raise ValueError("listHerd tool path not found in model context")
        
        import requests # Import requests library

        url = self.base_url + path
        headers = {
            'Authorization': f'Bearer {token}',
        }

        try:
            response = requests.get(url, headers=headers, timeout=10) # Added timeout
            response.raise_for_status()  # Raises HTTPError for 4XX/5XX responses
            return response.json()
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(f'HTTP error {exc.response.status_code}: {exc.response.reason}')
        except requests.exceptions.RequestException as exc:
            # This catches other exceptions like ConnectionError, Timeout, etc.
            raise RuntimeError(f'Request error: {exc}')
