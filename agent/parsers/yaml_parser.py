"""YAML context file parsers with fallback support."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


class YAMLParser:
    """YAML parser with fallback implementation."""
    
    @staticmethod
    def parse_context(path: str) -> Dict[str, Any]:
        """Parse the model context YAML file."""
        if YAML_AVAILABLE and yaml is not None:
            return YAMLParser._parse_with_pyyaml(path)
        else:
            logger.warning("PyYAML not available, using fallback parser")
            return YAMLParser._parse_fallback(path)
    
    @staticmethod
    def _parse_with_pyyaml(path: str) -> Dict[str, Any]:
        """Parse YAML using PyYAML library."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            
            if not isinstance(data, dict):
                raise ValueError("Model context must be a mapping")
            
            logger.debug(f"Parsed YAML context from {path} using PyYAML")
            return data
        
        except FileNotFoundError:
            logger.warning(f"Context file not found: {path}")
            return {"api": {"tools": []}}
        
        except yaml.YAMLError as exc:
            logger.error(f"Error parsing {path}: {exc}")
            raise ValueError(f"Error parsing {path}: {exc}") from exc
    
    @staticmethod
    def _parse_fallback(path: str) -> Dict[str, Any]:
        """Parse YAML using simple fallback parser."""
        context = {"api": {"tools": []}}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                current_tool = None
                
                for line_num, raw_line in enumerate(f, 1):
                    line = raw_line.strip()
                    
                    if not line or line.startswith("#"):
                        continue
                    
                    try:
                        if line.startswith("schema_version:"):
                            value = line.split(":", 1)[1].strip()
                            try:
                                context["schema_version"] = int(value)
                            except ValueError:
                                context["schema_version"] = value
                        
                        elif line.startswith("version:"):
                            context.setdefault("api", {})["version"] = line.split(":", 1)[1].strip()
                        
                        elif line.startswith("- name:"):
                            name = line.split(":", 1)[1].strip()
                            current_tool = {"name": name}
                            context["api"]["tools"].append(current_tool)
                        
                        elif current_tool is not None:
                            if line.startswith("method:"):
                                current_tool["method"] = line.split(":", 1)[1].strip()
                            elif line.startswith("path:"):
                                current_tool["path"] = line.split(":", 1)[1].strip()
                            elif line.startswith("description:"):
                                current_tool["description"] = line.split(":", 1)[1].strip()
                            elif line.startswith("scopes:"):
                                scopes_part = line.split(":", 1)[1].strip()
                                if scopes_part.startswith("[") and scopes_part.endswith("]"):
                                    # Parse simple list format: [scope1, scope2]
                                    scopes_str = scopes_part[1:-1]
                                    current_tool["scopes"] = [
                                        s.strip().strip('"\'') 
                                        for s in scopes_str.split(",") 
                                        if s.strip()
                                    ]
                    
                    except Exception as e:
                        logger.warning(f"Error parsing line {line_num} in {path}: {e}")
                        continue
            
            logger.debug(f"Parsed YAML context from {path} using fallback parser")
            return context
        
        except FileNotFoundError:
            logger.warning(f"Context file not found: {path}")
            return {"api": {"tools": []}}
        
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            return {"api": {"tools": []}}


class ContextValidator:
    """Validator for parsed context data."""
    
    @staticmethod
    def validate_context(context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize context data."""
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary")
        
        # Ensure api section exists
        if "api" not in context:
            context["api"] = {}
        
        # Ensure tools list exists
        if "tools" not in context["api"]:
            context["api"]["tools"] = []
        
        # Validate tools
        validated_tools = []
        for tool in context["api"]["tools"]:
            if ContextValidator._validate_tool(tool):
                validated_tools.append(tool)
        
        context["api"]["tools"] = validated_tools
        return context
    
    @staticmethod
    def _validate_tool(tool: Dict[str, Any]) -> bool:
        """Validate a single tool definition."""
        if not isinstance(tool, dict):
            logger.warning(f"Tool must be a dictionary, got {type(tool)}")
            return False
        
        if "name" not in tool:
            logger.warning("Tool missing required 'name' field")
            return False
        
        # Optional fields validation
        if "method" in tool and tool["method"] not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            logger.warning(f"Invalid HTTP method: {tool['method']}")
        
        if "path" in tool and not isinstance(tool["path"], str):
            logger.warning(f"Tool path must be a string: {tool['path']}")
        
        return True