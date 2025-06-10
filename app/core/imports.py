"""Centralized import management for better dependency control."""

from typing import TYPE_CHECKING

# Standard library imports
import asyncio
import logging
import os
import sys
import traceback
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from sqlite3 import Connection
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

# Third-party imports
from fastapi import FastAPI, Request, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel, Field, validator, root_validator
from pydantic_settings import BaseSettings

# Conditional imports for type checking
if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from openai import OpenAI

# Version constraints for critical dependencies
DEPENDENCY_VERSIONS = {
    "fastapi": ">=0.104.1,<1.0.0",
    "pydantic": ">=2.5.0,<3.0.0",
    "uvicorn": ">=0.24.0,<1.0.0",
    "httpx": ">=0.25.0,<1.0.0",
    "sqlalchemy": ">=2.0.0,<3.0.0",
    "openai": ">=1.0.0,<2.0.0"
}

# Import aliases for commonly used types
from typing import (
    Dict as DictType,
    List as ListType,
    Optional as OptionalType,
    Union as UnionType,
    Any as AnyType,
    Callable as CallableType,
    Awaitable as AwaitableType,
)

# Export commonly used imports
__all__ = [
    # Standard library
    "asyncio",
    "logging", 
    "os",
    "sys",
    "traceback",
    "asynccontextmanager",
    "datetime",
    "timedelta",
    "Enum",
    "Path",
    "Connection",
    "uuid4",
    
    # FastAPI
    "FastAPI",
    "Request",
    "Depends",
    "HTTPException",
    "status",
    "Header",
    "JSONResponse",
    "CORSMiddleware",
    "HTTPBearer",
    "HTTPAuthorizationCredentials",
    "OAuth2PasswordBearer",
    
    # Pydantic
    "BaseModel",
    "Field",
    "validator",
    "root_validator",
    "BaseSettings",
    
    # Security
    "CryptContext",
    
    # Type annotations
    "Any",
    "Dict",
    "List", 
    "Optional",
    "Union",
    "DictType",
    "ListType",
    "OptionalType",
    "UnionType",
    "AnyType",
    "CallableType",
    "AwaitableType",
    
    # Constants
    "DEPENDENCY_VERSIONS",
]


def check_dependency_versions() -> Dict[str, bool]:
    """Check if installed dependency versions match requirements."""
    import pkg_resources
    
    results = {}
    for package, version_spec in DEPENDENCY_VERSIONS.items():
        try:
            pkg_resources.require(f"{package}{version_spec}")
            results[package] = True
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            results[package] = False
    
    return results


def get_import_summary() -> Dict[str, Any]:
    """Get summary of import configuration."""
    return {
        "total_exports": len(__all__),
        "dependency_versions": DEPENDENCY_VERSIONS,
        "version_check": check_dependency_versions(),
    }