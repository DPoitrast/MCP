try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

# Import requests at module load so tests can patch MCPAgent.requests
import requests  # type: ignore
import openai
import os
from typing import List, Dict, Any, Optional


class MCPAgent:
    """Sophisticated agent for interacting with the MCP API with dynamic capability discovery."""

    def __init__(
        self, 
        base_url: str, 
        context_path: str = "model_context.yaml",
        auto_discover: bool = True,
        api_prefix: str = "/api/v1",
        timeout: float = 30.0,
        openai_api_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix
        self.timeout = timeout
        self.capabilities = {}
        
        # Initialize OpenAI client
        self.openai_client = None
        if openai_api_key or os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = openai.OpenAI(
                    api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
                )
                print("✓ OpenAI client initialized successfully")
            except Exception as e:
                print(f"⚠ Failed to initialize OpenAI client: {e}")
        
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

    def chat_with_openai(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        model: str = "gpt-4o-mini",
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a message to OpenAI and get a response.
        
        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            system_prompt: System prompt to guide the AI behavior
            model: OpenAI model to use
            
        Returns:
            Dict containing the response and updated conversation history
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Please provide an API key.")
        
        if conversation_history is None:
            conversation_history = []
        
        # Prepare messages
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                stream=stream
            )
            
            if stream:
                # Return generator for streaming
                def stream_generator():
                    full_response = ""
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            yield content
                    
                    # Update conversation history after streaming
                    updated_history = conversation_history.copy()
                    updated_history.append({"role": "user", "content": user_message})
                    updated_history.append({"role": "assistant", "content": full_response})
                    
                return {
                    "stream": stream_generator(),
                    "conversation_history": conversation_history,  # Will be updated after streaming
                    "is_streaming": True
                }
            else:
                assistant_response = response.choices[0].message.content
                
                # Update conversation history
                updated_history = conversation_history.copy()
                updated_history.append({"role": "user", "content": user_message})
                updated_history.append({"role": "assistant", "content": assistant_response})
                
                return {
                    "response": assistant_response,
                    "conversation_history": updated_history,
                    "usage": response.usage.model_dump() if response.usage else None,
                    "is_streaming": False
                }
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def intelligent_mcp_query(
        self, 
        user_request: str, 
        token: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Use OpenAI to understand user intent and execute MCP operations accordingly.
        
        Args:
            user_request: Natural language request from user
            token: Authentication token for MCP API
            conversation_history: Previous conversation context
            
        Returns:
            Dict containing the response and any MCP operation results
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Please provide an API key.")
        
        # Get available tools for context
        available_tools = self.get_available_tools()
        tools_description = "\n".join([
            f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}"
            for tool in available_tools
        ])
        
        system_prompt = f"""You are an intelligent MCP (Model Context Protocol) agent assistant. 
You have access to the following MCP API tools:

{tools_description}

Your job is to:
1. Understand the user's natural language request
2. Determine which MCP API tool(s) to use
3. Extract any necessary parameters
4. Provide a helpful response

If the user asks for something that requires an MCP API call, respond with a JSON object containing:
- "action": "mcp_call"
- "tool_name": the name of the tool to use
- "parameters": object with the required parameters
- "explanation": brief explanation of what you're doing

If the user asks a general question or needs clarification, respond normally as a helpful assistant.

Current conversation context: The user is interacting with an MCP system that manages herds and other resources."""

        # Get OpenAI's interpretation of the request
        chat_response = self.chat_with_openai(
            user_message=user_request,
            conversation_history=conversation_history,
            system_prompt=system_prompt,
            model="gpt-4o-mini"
        )
        
        assistant_response = chat_response["response"]
        
        # Try to parse if this is an MCP action request
        try:
            import json
            # Look for JSON in the response
            if "action" in assistant_response and "mcp_call" in assistant_response:
                # Extract JSON from response
                start = assistant_response.find("{")
                end = assistant_response.rfind("}") + 1
                if start != -1 and end != 0:
                    action_data = json.loads(assistant_response[start:end])
                    
                    if action_data.get("action") == "mcp_call":
                        tool_name = action_data.get("tool_name")
                        parameters = action_data.get("parameters", {})
                        explanation = action_data.get("explanation", "")
                        
                        # Execute the MCP operation
                        try:
                            mcp_result = self.execute_operation(tool_name, token, **parameters)
                            
                            # Format the response
                            formatted_response = f"{explanation}\n\nResults:\n{json.dumps(mcp_result, indent=2)}"
                            
                            return {
                                "response": formatted_response,
                                "mcp_result": mcp_result,
                                "conversation_history": chat_response["conversation_history"],
                                "action_taken": {
                                    "tool": tool_name,
                                    "parameters": parameters
                                }
                            }
                        except Exception as e:
                            error_response = f"{explanation}\n\nError executing MCP operation: {str(e)}"
                            return {
                                "response": error_response,
                                "error": str(e),
                                "conversation_history": chat_response["conversation_history"]
                            }
        except:
            # If parsing fails, treat as normal conversation
            pass
        
        # Return normal chat response
        return {
            "response": assistant_response,
            "conversation_history": chat_response["conversation_history"]
        }
