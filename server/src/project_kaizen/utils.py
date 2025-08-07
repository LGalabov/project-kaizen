"""
Utility functions for Project Kaizen MCP Server.

This module provides common utility functions used across the application.
"""

from typing import Literal, cast


def parse_transport(value: str | None, default: str = "stdio") -> Literal["stdio", "http"]:
    """
    Parse and return a validated transport value.

    Args:
        value: The transport value to validate
        default: Default value if value is None

    Returns:
        Valid transport literal

    Raises:
        ValueError: If transport value is invalid
    """
    transport = value if value is not None else default

    if transport not in ("stdio", "http"):
        raise ValueError(f"Invalid transport: {transport}. Must be 'stdio' or 'http'")

    # Type narrowing - at this point we know it's a valid literal
    return cast(Literal["stdio", "http"], transport)


def parse_scope(scope: str) -> tuple[str, str]:
    """
    Parse canonical scope identifier into namespace and scope name.

    Args:
        scope: Canonical scope identifier (namespace:scope)

    Returns:
        Tuple of (namespace, scope_name)

    Raises:
        ValueError: If scope format is invalid
    """
    if ":" not in scope:
        raise ValueError("Scope must be in format 'namespace:scope'")

    namespace, scope_name = scope.split(":", 1)
    return namespace, scope_name
