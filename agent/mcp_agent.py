try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

# Import requests at module load so tests can patch MCPAgent.requests
import requests  # type: ignore


class MCPAgent:
    """Sophisticated agent for interacting with the MCP API with dynamic capability discovery."""

    def __init__(
        self, 
        base_url: str, 
        context_path: str = "model_context.yaml",
        auto_discover: bool = True,
        api_prefix: str = "/api/v1",
        timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix
        self.timeout = timeout
        self.capabilities = {}
        
        # Try dynamic discovery first, fall back to static context
        if auto_discover:
            try:
                self.capabilities = self._discover_capabilities()
                print(f"✓ Discovered {len(self.capabilities.get('paths', {}))} API endpoints dynamically")
            except Exception as e:
                print(f"⚠ Dynamic discovery failed ({e}), falling back to static context")
                self.context = self._parse_context(context_path)
        else:
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
                    if line.startswith("schema_version:"):
                        # Top level schema version
                        value = line.split(":", 1)[1].strip()
                        try:
                            context["schema_version"] = int(value)
                        except ValueError:
                            context["schema_version"] = value
                    if line.startswith("version:"):
                        context.setdefault("api", {})["version"] = line.split(":", 1)[
                            1
                        ].strip()
                    elif line.startswith("- name:"):
                        name = line.split(":", 1)[1].strip()
                        tool = {"name": name}
                        context["api"]["tools"].append(tool)
                    elif line.startswith("method:") and tool is not None:
                        tool["method"] = line.split(":", 1)[1].strip()
                    elif line.startswith("path:") and tool is not None:
                        tool["path"] = line.split(":", 1)[1].strip()
                    elif line.startswith("description:") and tool is not None:
                        tool["description"] = line.split(":", 1)[1].strip()
                    elif line.startswith("scopes:") and tool is not None:
                        scopes_part = line.split(":", 1)[1].strip()
                        scopes_part = scopes_part.strip("[]")
                        scopes = [
                            s.strip() for s in scopes_part.split(",") if s.strip()
                        ]
                        tool["scopes"] = scopes if scopes_part else []
        except FileNotFoundError:
            # If the file is not found, return the default context,
            # which is an empty list of tools. This matches the behavior
            # of the original PyYAML based parser.
            pass
        return context

    def _discover_capabilities(self) -> dict:
        """Discover API capabilities through OpenAPI metadata."""
        openapi_url = f"{self.base_url}{self.api_prefix}/openapi.json"
        
        try:
            response = requests.get(openapi_url, timeout=self.timeout)
            response.raise_for_status()
            openapi_spec = response.json()
            
            # Parse OpenAPI spec into our internal format
            capabilities = {
                "info": openapi_spec.get("info", {}),
                "servers": openapi_spec.get("servers", []),
                "paths": {},
                "tools": []
            }
            
            # Convert OpenAPI paths to our tool format
            for path, methods in openapi_spec.get("paths", {}).items():
                capabilities["paths"][path] = methods
                
                for method, details in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        tool = {
                            "name": self._generate_tool_name(method, path, details),
                            "method": method.upper(),
                            "path": path,
                            "description": details.get("summary", details.get("description", "")),
                            "parameters": self._extract_parameters(details),
                            "responses": details.get("responses", {}),
                            "tags": details.get("tags", [])
                        }
                        capabilities["tools"].append(tool)
            
            return capabilities
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch OpenAPI spec from {openapi_url}: {e}")
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Invalid OpenAPI specification: {e}")

    def _generate_tool_name(self, method: str, path: str, details: dict) -> str:
        """Generate a descriptive tool name from OpenAPI operation."""
        # Use operationId if available
        if "operationId" in details:
            return details["operationId"]
        
        # Generate name from method and path
        path_parts = [part for part in path.split("/") if part and not part.startswith("{")]
        if path_parts:
            resource = path_parts[-1]
        else:
            resource = "unknown"
        
        method_map = {
            "GET": "list" if "{" not in path else "get",
            "POST": "create",
            "PUT": "update", 
            "DELETE": "delete",
            "PATCH": "patch"
        }
        
        action = method_map.get(method.upper(), method.lower())
        return f"{action}_{resource}"

    def _extract_parameters(self, operation_details: dict) -> list:
        """Extract parameter information from OpenAPI operation."""
        parameters = []
        
        # Path parameters
        for param in operation_details.get("parameters", []):
            parameters.append({
                "name": param.get("name"),
                "in": param.get("in"),
                "required": param.get("required", False),
                "type": param.get("schema", {}).get("type", "string"),
                "description": param.get("description", "")
            })
        
        # Request body (for POST/PUT operations)
        if "requestBody" in operation_details:
            req_body = operation_details["requestBody"]
            content = req_body.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                parameters.append({
                    "name": "body",
                    "in": "body", 
                    "required": req_body.get("required", False),
                    "schema": schema,
                    "description": req_body.get("description", "Request body")
                })
        
        return parameters

    def get_available_tools(self) -> list:
        """Get list of all available tools/operations."""
        if hasattr(self, 'capabilities') and self.capabilities:
            return self.capabilities.get("tools", [])
        else:
            # Fallback to static context
            api_tools = self.context.get("api", {}).get("tools", [])
            return api_tools

    def find_tool(self, tool_name: str) -> dict:
        """Find a specific tool by name."""
        for tool in self.get_available_tools():
            if tool.get("name") == tool_name:
                return tool
        return None

    def execute_operation(self, tool_name: str, token: str, **kwargs) -> dict:
        """Execute any discovered operation by tool name."""
        tool = self.find_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in discovered capabilities")
        
        method = tool.get("method", "GET")
        path = tool.get("path", "")
        
        # Replace path parameters
        for key, value in kwargs.items():
            if f"{{{key}}}" in path:
                path = path.replace(f"{{{key}}}", str(value))
        
        url = self.base_url + path
        headers = {"Authorization": f"Bearer {token}"}
        
        # Prepare request based on method
        request_kwargs = {"headers": headers}
        
        if method in ["POST", "PUT", "PATCH"]:
            # Extract body data from kwargs
            body_data = {k: v for k, v in kwargs.items() if f"{{{k}}}" not in tool.get("path", "")}
            if body_data:
                request_kwargs["json"] = body_data
        elif method == "GET":
            # Extract query parameters
            query_params = {k: v for k, v in kwargs.items() if f"{{{k}}}" not in tool.get("path", "")}
            if query_params:
                request_kwargs["params"] = query_params
        
        # Add timeout to request
        request_kwargs["timeout"] = self.timeout
        
        try:
            response = requests.request(method, url, **request_kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as exc:
            raise RuntimeError(f"Request timeout after {self.timeout}s: {exc}")
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(f"HTTP error {exc.response.status_code}: {exc.response.reason}")
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Request error: {exc}")

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

        url = self.base_url + path
        headers = {
            "Authorization": f"Bearer {token}",
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()  # Raises HTTPError for 4XX/5XX responses
            return response.json()
        except requests.exceptions.Timeout as exc:
            raise RuntimeError(f"Request timeout after {self.timeout}s: {exc}")
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"HTTP error {exc.response.status_code}: {exc.response.reason}"
            )
        except requests.exceptions.RequestException as exc:
            # This catches other exceptions like ConnectionError, Timeout, etc.
            raise RuntimeError(f"Request error: {exc}")
