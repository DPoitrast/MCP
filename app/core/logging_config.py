"""Enhanced logging configuration for structured logging."""

import json
import logging
import logging.config
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from .config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with JSON output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None
            }
        
        # Add extra fields from the record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                'filename', 'module', 'lineno', 'funcName', 'created', 
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info'
            }:
                extra_fields[key] = value
        
        if extra_fields:
            log_data["extra"] = extra_fields
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output in development."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if not sys.stderr.isatty():
            # No colors for non-terminal output
            return super().format(record)
        
        color = self.COLORS.get(record.levelname, '')
        reset = self.RESET
        
        # Color the level name
        original_levelname = record.levelname
        record.levelname = f"{color}{record.levelname}{reset}"
        
        try:
            formatted = super().format(record)
        finally:
            # Restore original level name
            record.levelname = original_levelname
        
        return formatted


def setup_logging() -> None:
    """Set up logging configuration based on environment."""
    
    # Determine log level
    log_level = getattr(logging, settings.log_level.value.upper())
    
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
            },
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "colored" if settings.is_development else "simple",
                "stream": sys.stderr,
            },
        },
        "loggers": {
            # Application loggers
            "app": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "agent": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Third-party loggers
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO" if settings.debug else "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"], 
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "INFO" if settings.database.echo else "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }
    
    # Add file logging for production
    if settings.is_production:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "structured",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            logger_config["handlers"].append("file")
        config["root"]["handlers"].append("file")
    
    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> None:
    """Log a message with additional context."""
    if context:
        kwargs.update(context)
    
    logger.log(level, message, extra=kwargs)


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration: float,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Log performance metrics."""
    log_data = {
        "operation": operation,
        "duration_ms": round(duration * 1000, 2),
        "performance_metric": True,
    }
    
    if context:
        log_data.update(context)
    
    logger.info(f"Performance: {operation} completed in {duration:.3f}s", extra=log_data)


def log_security_event(
    logger: logging.Logger,
    event_type: str,
    details: Dict[str, Any],
    severity: str = "medium"
) -> None:
    """Log security-related events."""
    log_data = {
        "security_event": True,
        "event_type": event_type,
        "severity": severity,
        "details": details,
    }
    
    logger.warning(f"Security event: {event_type}", extra=log_data)