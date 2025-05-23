"""Custom exception classes for the MCP application."""


class MCPException(Exception):
    """Base exception class for MCP application."""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class HerdNotFoundError(MCPException):
    """Raised when a herd is not found."""

    def __init__(self, herd_id: int):
        message = f"Herd with ID {herd_id} not found"
        super().__init__(message, "HERD_NOT_FOUND")


class ValidationError(MCPException):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str):
        full_message = f"Validation error for field '{field}': {message}"
        super().__init__(full_message, "VALIDATION_ERROR")


class DatabaseError(MCPException):
    """Raised when database operations fail."""

    def __init__(self, operation: str, original_error: Exception = None):
        message = f"Database operation '{operation}' failed"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message, "DATABASE_ERROR")


class AuthenticationError(MCPException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")
