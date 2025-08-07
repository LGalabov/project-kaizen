"""
Validation functions for Project Kaizen MCP Server.

This module provides validation functions for all input parameters
used in the MCP server.
"""

import re

# Regular expressions for validation
NAMESPACE_PATTERN = re.compile(r"^[a-z0-9\-_]+$")
SCOPE_NAME_PATTERN = re.compile(r"^[a-z0-9\-_]+$")

# Valid enum values
VALID_STYLES = {"short", "long", "details"}
VALID_TASK_SIZES = {"XS", "S", "M", "L", "XL"}


def validate_namespace(name: str | None) -> None:
    """
    Validates namespace or scope name format (2-64 chars, lowercase/digits/-/_).
    Accepts None/empty values.

    @throws ValueError: if name contains invalid characters or wrong length
    """
    if not name:
        return

    if len(name) < 2 or len(name) > 64:
        raise ValueError("Name must be 2-64 characters")

    if not NAMESPACE_PATTERN.match(name):
        raise ValueError(
            "Name must contain only lowercase letters, numbers, hyphens, and underscores"
        )


def validate_description(description: str | None) -> None:
    """
    Validates description is 2-64 chars and not just whitespace.
    Accepts None/empty values.

    @throws ValueError: if description is just whitespace or wrong length
    """
    if not description:
        return

    if not description.strip():
        raise ValueError("Description cannot be just whitespace")

    if len(description) < 2 or len(description) > 64:
        raise ValueError("Description must be 2-64 characters")


def validate_scope(scope: str | None) -> None:
    """
    Validates canonical scope format 'namespace:scope' (5-129 chars total).
    Accepts None/empty values.

    @throws ValueError: if format is invalid or parts don't meet requirements
    """
    if not scope:
        return

    if len(scope) < 5 or len(scope) > 129:
        raise ValueError("Scope identifier must be 5-129 characters")

    if ":" not in scope:
        raise ValueError("Scope must be in format 'namespace:scope'")

    namespace, scope_name = scope.split(":", 1)

    # Validate both parts - they will handle empty strings
    if not namespace or len(namespace) < 2 or len(namespace) > 64:
        raise ValueError("Namespace part must be 2-64 characters")
    if not NAMESPACE_PATTERN.match(namespace):
        raise ValueError(
            "Namespace part must contain only lowercase letters, numbers, hyphens, and underscores"
        )

    if not scope_name or len(scope_name) < 2 or len(scope_name) > 64:
        raise ValueError("Scope name part must be 2-64 characters")
    if not SCOPE_NAME_PATTERN.match(scope_name):
        raise ValueError(
            "Scope name part must contain only lowercase letters, numbers, hyphens, and underscores"
        )


def validate_content(content: str | None) -> None:
    """
    Validates knowledge content is not just whitespace.
    Accepts None/empty values.

    @throws ValueError: if content is only whitespace
    """
    if not content:
        return

    if not content.strip():
        raise ValueError("Knowledge content cannot be just whitespace")


def validate_context(context: str | None) -> None:
    """
    Validates knowledge context is not just whitespace.
    Accepts None/empty values.

    @throws ValueError: if context is only whitespace
    """
    if not context:
        return

    if not context.strip():
        raise ValueError("Knowledge context cannot be just whitespace")


def validate_style(style: str | None) -> None:
    """
    Validates style is one of: 'short', 'long', 'details'.
    Accepts None/empty values.

    @throws ValueError: if style is not a valid option
    """
    if not style:
        return

    if style not in VALID_STYLES:
        raise ValueError(f"Style must be one of: {', '.join(sorted(VALID_STYLES))}")


def validate_task_size(task_size: str | None) -> None:
    """
    Validates task size is one of: 'XS', 'S', 'M', 'L', 'XL'.
    Accepts None/empty values.

    @throws ValueError: if task_size is not a valid option
    """
    if not task_size:
        return

    if task_size not in VALID_TASK_SIZES:
        raise ValueError(f"Task size must be one of: {', '.join(sorted(VALID_TASK_SIZES))}")
