class MCPAgent:
    """Simple agent for interacting with the MCP API."""

    def __init__(self, base_url: str, context_path: str = "model_context.yaml"):
        self.base_url = base_url.rstrip('/')
        self.context = self._parse_context(context_path)

    @staticmethod
    def _parse_context(path: str) -> dict:
        """Parse a tiny YAML file describing the API."""
        context = {"api": {"tools": []}}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                tool = None
                for raw_line in f:
                    line = raw_line.strip()
                    if line.startswith('version:'):
                        context.setdefault('api', {})['version'] = line.split(':', 1)[1].strip()
                    elif line.startswith('- name:'):
                        name = line.split(':', 1)[1].strip()
                        tool = {"name": name}
                        context['api']['tools'].append(tool)
                    elif line.startswith('method:') and tool is not None:
                        tool['method'] = line.split(':', 1)[1].strip()
                    elif line.startswith('path:') and tool is not None:
                        tool['path'] = line.split(':', 1)[1].strip()
        except FileNotFoundError:
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
        import json
        from urllib import request, error

        req = request.Request(
            self.base_url + path,
            headers={
                'Authorization': f'Bearer {token}',
            },
        )
        try:
            with request.urlopen(req) as resp:
                body = resp.read()
                return json.loads(body.decode('utf-8'))
        except error.HTTPError as exc:
            raise RuntimeError(f'HTTP error {exc.code}: {exc.reason}')
