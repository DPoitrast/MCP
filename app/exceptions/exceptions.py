"""Enhanced exception classes for the MCP application with improved error handling."""

import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for better classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    CONFIGURATION = "configuration"


class MCPException(Exception):
    """Enhanced base exception class for MCP application with structured error handling."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.user_message = user_message or message
        self.original_error = original_error
        self.context = context or {}
        self.error_id = str(uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        self.traceback = traceback.format_exc() if original_error else None
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for structured logging."""
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "context": self.context,
            "timestamp": self.timestamp,
            "original_error": str(self.original_error) if self.original_error else None,
            "traceback": self.traceback
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class ValidationError(MCPException):
    """Raised when input validation fails."""

    def __init__(
        self,
        field: str,
        message: str,
        value: Any = None,
        constraints: Optional[List[str]] = None
    ):
        full_message = f"Validation error for field '{field}': {message}"
        details = {
            "field": field,
            "value": value,
            "constraints": constraints or []
        }
        user_message = f"Invalid value for {field}: {message}"
        
        super().__init__(
            message=full_message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            user_message=user_message
        )


class BusinessLogicError(MCPException):
    """Raised when business logic constraints are violated."""

    def __init__(
        self,
        message: str,
        rule: str,
        context: Optional[Dict[str, Any]] = None
    ):
        details = {"business_rule": rule}
        
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            context=context
        )


class DatabaseError(MCPException):
    """Raised when database operations fail."""

    def __init__(
        self,
        operation: str,
        original_error: Optional[Exception] = None,
        entity: Optional[str] = None,
        entity_id: Optional[Union[int, str]] = None
    ):
        message = f"Database operation '{operation}' failed"
        if entity:
            message += f" for {entity}"
            if entity_id:
                message += f" with ID {entity_id}"
        
        details = {
            "operation": operation,
            "entity": entity,
            "entity_id": entity_id
        }
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            details=details,
            user_message="A database error occurred. Please try again.",
            original_error=original_error
        )


class AuthenticationError(MCPException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        reason: Optional[str] = None,
        username: Optional[str] = None
    ):
        details = {
            "reason": reason,
            "username": username
        }
        
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            user_message="Authentication failed. Please check your credentials."
        )


class AuthorizationError(MCPException):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Access denied",
        required_permission: Optional[str] = None,
        resource: Optional[str] = None,
        username: Optional[str] = None
    ):
        details = {
            "required_permission": required_permission,
            "resource": resource,
            "username": username
        }
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            user_message="You don't have permission to access this resource."
        )


class ResourceNotFoundError(MCPException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        identifier: Union[int, str],
        identifier_type: str = "ID"
    ):
        message = f"{resource_type} with {identifier_type} '{identifier}' not found"
        details = {
            "resource_type": resource_type,
            "identifier": identifier,
            "identifier_type": identifier_type
        }
        
        super().__init__(
            message=message,
            error_code=f"{resource_type.upper()}_NOT_FOUND",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.LOW,
            details=details,
            user_message=f"The requested {resource_type.lower()} was not found."
        )


class ResourceAlreadyExistsError(MCPException):
    """Raised when trying to create a resource that already exists."""

    def __init__(
        self,
        resource_type: str,
        identifier: Union[int, str],
        identifier_type: str = "ID"
    ):
        message = f"{resource_type} with {identifier_type} '{identifier}' already exists"
        details = {
            "resource_type": resource_type,
            "identifier": identifier,
            "identifier_type": identifier_type
        }
        
        super().__init__(
            message=message,
            error_code=f"{resource_type.upper()}_ALREADY_EXISTS",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.LOW,
            details=details,
            user_message=f"A {resource_type.lower()} with this {identifier_type.lower()} already exists."
        )


class ExternalServiceError(MCPException):
    """Raised when external service calls fail."""

    def __init__(
        self,
        service_name: str,
        operation: str,
        original_error: Optional[Exception] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        message = f"External service '{service_name}' operation '{operation}' failed"
        details = {
            "service_name": service_name,
            "operation": operation,
            "status_code": status_code,
            "response_data": response_data
        }
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.HIGH,
            details=details,
            user_message="An external service is currently unavailable. Please try again later.",
            original_error=original_error
        )


class ConfigurationError(MCPException):
    """Raised when configuration is invalid or missing."""

    def __init__(
        self,
        config_key: str,
        message: str,
        expected_type: Optional[str] = None,
        current_value: Any = None
    ):
        full_message = f"Configuration error for '{config_key}': {message}"
        details = {
            "config_key": config_key,
            "expected_type": expected_type,
            "current_value": current_value
        }
        
        super().__init__(
            message=full_message,
            error_code="CONFIGURATION_ERROR",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            user_message="System configuration error. Please contact support."
        )


# Backward compatibility aliases
HerdNotFoundError = lambda herd_id: ResourceNotFoundError("Herd", herd_id)
UserNotFoundError = lambda username=None, user_id=None: ResourceNotFoundError(
    "User", 
    username or user_id, 
    "username" if username else "ID"
)
UserAlreadyExistsError = lambda username: ResourceAlreadyExistsError("User", username, "username")
