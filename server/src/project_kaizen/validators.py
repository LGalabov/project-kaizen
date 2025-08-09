"""
Validation functions for Project Kaizen MCP Server.

This module provides validation functions for all input parameters
used in the MCP server.
"""

import re

# Regular expressions for validation
NAMESPACE_PATTERN = re.compile(r"^[a-z0-9\-]+$")
SCOPE_NAME_PATTERN = re.compile(r"^[a-z0-9\-]+$")

# Valid enum values
VALID_TASK_SIZES = {"XS", "S", "M", "L", "XL"}


def validate_namespace_name(namespace_name: str | None) -> None:
    """
    Validates the namespace name format (2-64 chars, lowercase/digits/-).

    Raises:
        ValueError: if namespace_name contains invalid characters or a wrong length
    """
    if not namespace_name:
        raise ValueError("Namespace name cannot be empty")

    if len(namespace_name) < 2 or len(namespace_name) > 64:
        raise ValueError("Namespace name must be 2-64 characters")

    if not NAMESPACE_PATTERN.match(namespace_name):
        raise ValueError("Namespace name must contain only lowercase letters, numbers, and hyphens")


def validate_scope_name(scope_name: str | None) -> None:
    """
    Validates the scope name format (2-64 chars, lowercase/digits/-).

    Raises:
        ValueError: if scope_name contains invalid characters or a wrong length
    """
    if not scope_name:
        raise ValueError("Scope name cannot be empty")

    if len(scope_name) < 2 or len(scope_name) > 64:
        raise ValueError("Scope name must be 2-64 characters")

    if not SCOPE_NAME_PATTERN.match(scope_name):
        raise ValueError("Scope name must contain only lowercase letters, numbers, and hyphens")


def validate_canonical_scope_name(canonical_scope_name: str | None) -> None:
    """
    Validates canonical scope name format 'namespace:scope' (5-129 chars total).
    Accepts None/empty values.

    Raises:
        ValueError: if the format is invalid, or parts don't meet requirements
    """
    if not canonical_scope_name:
        return

    if len(canonical_scope_name) < 5 or len(canonical_scope_name) > 129:
        raise ValueError("Canonical scope name must be 5-129 characters")

    if ":" not in canonical_scope_name:
        raise ValueError("Canonical scope name must be in format 'namespace:scope'")

    namespace_name, scope_name = canonical_scope_name.split(":", 1)

    # Delegate to individual validators
    validate_namespace_name(namespace_name)
    validate_scope_name(scope_name)


def validate_description(description: str | None) -> None:
    """
    Validates description is 2-64 chars and not just whitespace.
    Accepts None/empty values.

    Raises:
        ValueError: if the description is just whitespace or wrong length
    """
    if not description:
        return

    if not description.strip():
        raise ValueError("Description cannot be just whitespace")

    if len(description) < 2 or len(description) > 64:
        raise ValueError("Description must be 2-64 characters")


def validate_content(content: str | None) -> None:
    """
    Validates knowledge content is not just whitespace.
    Accepts None/empty values.

    Raises:
        ValueError: if content is only whitespace
    """
    if not content:
        return

    if not content.strip():
        raise ValueError("Knowledge content cannot be just whitespace")


def validate_context(context: str | None) -> None:
    """
    Validates knowledge context is not just whitespace.
    Accepts None/empty values.

    Raises:
        ValueError: if context is only whitespace
    """
    if not context:
        return

    if not context.strip():
        raise ValueError("Knowledge context cannot be just whitespace")


def validate_task_size(task_size: str | None) -> None:
    """
    Validates task size is one of: 'XS', 'S', 'M', 'L', 'XL'.
    Accepts None/empty values.

    Raises:
        ValueError: if task_size is not a valid option
    """
    if not task_size:
        return

    if task_size not in VALID_TASK_SIZES:
        raise ValueError(f"Task size must be one of: {', '.join(sorted(VALID_TASK_SIZES))}")
