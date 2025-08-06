"""
Data models and validation for Project Kaizen MCP Server.

This module provides Pydantic models and validation functions for all
data structures used in the MCP server.
"""

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Regular expressions for validation
NAMESPACE_PATTERN = re.compile(r"^[a-z0-9\-_]+$")
SCOPE_NAME_PATTERN = re.compile(r"^[a-z0-9\-_]+$")


class NamespaceModel(BaseModel):
    """Model for namespace data."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=64,
        description="Namespace name (lowercase, alphanumeric, hyphens, underscores)",
    )
    description: str = Field(
        ..., min_length=2, max_length=64, description="Human-readable namespace description"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate namespace name format."""
        if not NAMESPACE_PATTERN.match(v):
            raise ValueError(
                "Namespace name must contain only lowercase letters, "
                "numbers, hyphens, and underscores"
            )
        return v


class ScopeModel(BaseModel):
    """Model for scope data."""

    scope: str = Field(
        ...,
        min_length=5,
        max_length=129,
        description="Full scope identifier (namespace:scope_name)",
    )
    description: str = Field(
        ..., min_length=2, max_length=64, description="Human-readable scope description"
    )
    parents: list[str] = Field(default_factory=list, description="Parent scope identifiers")

    @field_validator("scope")
    @classmethod
    def validate_scope_format(cls, v: str) -> str:
        """Validate scope identifier format."""
        if ":" not in v:
            raise ValueError("Scope must be in format 'namespace:scope_name'")

        namespace, scope_name = v.split(":", 1)

        # Validate namespace part
        if len(namespace) < 2 or len(namespace) > 64:
            raise ValueError("Namespace part must be 2-64 characters")
        if not NAMESPACE_PATTERN.match(namespace):
            raise ValueError(
                "Namespace part must contain only lowercase letters, "
                "numbers, hyphens, and underscores"
            )

        # Validate scope name part
        if len(scope_name) < 2 or len(scope_name) > 64:
            raise ValueError("Scope name part must be 2-64 characters")
        if not SCOPE_NAME_PATTERN.match(scope_name):
            raise ValueError(
                "Scope name must contain only lowercase letters, numbers, hyphens, and underscores"
            )

        return v

    @field_validator("parents")
    @classmethod
    def validate_parents(cls, v: list[str]) -> list[str]:
        """Validate parent scope identifiers."""
        for parent in v:
            if ":" not in parent:
                raise ValueError(f"Parent '{parent}' must be in format 'namespace:scope_name'")
        return v


class KnowledgeModel(BaseModel):
    """Model for knowledge entry data."""

    scope: str = Field(
        ...,
        min_length=5,
        max_length=129,
        description="Target scope identifier (namespace:scope_name)",
    )
    content: str = Field(..., min_length=1, description="Knowledge content to store")
    context: str = Field(..., min_length=1, description="Context or summary for searchability")

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        """Validate scope identifier."""
        if ":" not in v:
            raise ValueError("Scope must be in format 'namespace:scope_name'")
        return v

    @field_validator("content", "context")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure content and context are not just whitespace."""
        if not v.strip():
            raise ValueError("Field cannot be empty or just whitespace")
        return v


class SearchQueryModel(BaseModel):
    """Model for search query parameters."""

    queries: list[str] = Field(..., min_length=1, description="Multiple targeted search queries")
    scope: str | None = Field(
        None, min_length=5, max_length=129, description="Optional scope to limit search"
    )
    task_size: Literal["XS", "S", "M", "L", "XL"] | None = Field(
        None, description="Task complexity for filtering"
    )

    @field_validator("queries")
    @classmethod
    def validate_queries(cls, v: list[str]) -> list[str]:
        """Validate search queries."""
        if not v:
            raise ValueError("At least one query is required")

        # Ensure queries are not empty
        for query in v:
            if not query.strip():
                raise ValueError("Query cannot be empty or just whitespace")

        return v

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str | None) -> str | None:
        """Validate optional scope identifier."""
        if v and ":" not in v:
            raise ValueError("Scope must be in format 'namespace:scope_name'")
        return v


# Standalone validation functions for use in server.py


def validate_namespace(name: str) -> None:
    """
    Validate namespace name format.

    Args:
        name: Namespace name to validate

    Raises:
        ValueError: If namespace name is invalid
    """
    if not name or len(name) < 2 or len(name) > 64:
        raise ValueError("Namespace name must be 2-64 characters")

    if not NAMESPACE_PATTERN.match(name):
        raise ValueError(
            "Namespace name must contain only lowercase letters, numbers, hyphens, and underscores"
        )


def validate_scope(scope: str) -> None:
    """
    Validate scope identifier format.

    Args:
        scope: Scope identifier to validate

    Raises:
        ValueError: If scope identifier is invalid
    """
    if not scope or len(scope) < 5 or len(scope) > 129:
        raise ValueError("Scope identifier must be 5-129 characters")

    if ":" not in scope:
        raise ValueError("Scope must be in format 'namespace:scope_name'")

    namespace, scope_name = scope.split(":", 1)

    # Validate namespace part
    validate_namespace(namespace)

    # Validate scope name part
    if not scope_name or len(scope_name) < 2 or len(scope_name) > 64:
        raise ValueError("Scope name must be 2-64 characters")

    if not SCOPE_NAME_PATTERN.match(scope_name):
        raise ValueError(
            "Scope name must contain only lowercase letters, numbers, hyphens, and underscores"
        )


def validate_knowledge(content: str, context: str) -> None:
    """
    Validate knowledge entry fields.

    Args:
        content: Knowledge content
        context: Knowledge context for searchability

    Raises:
        ValueError: If fields are invalid
    """
    if not content or not content.strip():
        raise ValueError("Knowledge content cannot be empty")

    if not context or not context.strip():
        raise ValueError("Knowledge context cannot be empty")


def parse_scope(scope: str) -> tuple[str, str]:
    """
    Parse scope identifier into namespace and scope name.

    Args:
        scope: Full scope identifier

    Returns:
        Tuple of (namespace, scope_name)

    Raises:
        ValueError: If scope format is invalid
    """
    if ":" not in scope:
        raise ValueError("Scope must be in format 'namespace:scope_name'")

    namespace, scope_name = scope.split(":", 1)
    return namespace, scope_name
