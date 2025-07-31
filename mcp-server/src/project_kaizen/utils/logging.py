"""Structured logging configuration for Project Kaizen MCP server."""

import logging
import sys
from typing import Any, cast

import structlog

from ..config import settings


def configure_logging() -> None:
    """Configure structured logging with JSON output for MCP server."""

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    # Configure structlog processors
    processors: list[structlog.types.Processor] = [
        # Add timestamp to all log entries
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),

        # Add caller information in debug mode
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.FILENAME,
                       structlog.processors.CallsiteParameter.LINENO]
        ) if settings.debug else structlog.processors.CallsiteParameterAdder(parameters=[]),

        # Format as JSON for structured logging
        structlog.processors.JSONRenderer(),
    ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name, typically __name__

    Returns:
        Configured structured logger
    """
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))


def log_mcp_tool_call(tool_name: str, **kwargs: Any) -> None:
    """Log MCP tool invocation with structured context.

    Args:
        tool_name: Name of the MCP tool being called
        **kwargs: Additional context to log
    """
    logger = get_logger("mcp.tools")
    logger.info(
        "MCP tool called",
        tool=tool_name,
        **kwargs
    )


def log_database_operation(operation: str, **kwargs: Any) -> None:
    """Log database operation with structured context.

    Args:
        operation: Database operation name (SELECT, INSERT, etc.)
        **kwargs: Additional context to log (query, params, execution_time, etc.)
    """
    logger = get_logger("database")
    logger.info(
        "Database operation",
        operation=operation,
        **kwargs
    )


def log_error_with_context(error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log error with structured context information.

    Args:
        error: Exception that occurred
        context: Additional context dictionary
    """
    logger = get_logger("errors")
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        **(context or {})
    )
