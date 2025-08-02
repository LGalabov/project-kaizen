"""Simple Python logging configuration for Project Kaizen MCP server."""

import logging
import sys
from typing import Any

from ..settings import settings


def configure_logging() -> None:
    """Configure simple Python logging for MCP server."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name, typically __name__

    Returns:
        Configured logger
    """
    return logging.getLogger(name)


def log_mcp_tool_call(tool_name: str, **kwargs: Any) -> None:
    """Log MCP tool invocation with context.

    Args:
        tool_name: Name of the MCP tool being called
        **kwargs: Additional context to log
    """
    logger = get_logger("project-kaizen.mcp.tools")
    extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
    logger.info(f"MCP tool called: {tool_name} {extra_info}".strip())


def log_database_operation(operation: str, **kwargs: Any) -> None:
    """Log database operation with context.

    Args:
        operation: Database operation name (SELECT, INSERT, etc.)
        **kwargs: Additional context to log (query, params, execution_time, etc.)
    """
    logger = get_logger("project-kaizen.database")
    extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
    logger.info(f"Database operation: {operation} {extra_info}".strip())


def log_error_with_context(
    error: Exception, context: dict[str, Any] | None = None
) -> None:
    """Log error with context information.

    Args:
        error: Exception that occurred
        context: Additional context dictionary
    """
    logger = get_logger("project-kaizen.errors")
    context_info = " ".join(f"{k}={v}" for k, v in (context or {}).items())
    logger.error(
        f"Error occurred: {type(error).__name__}: {error} {context_info}".strip(),
        exc_info=True
    )