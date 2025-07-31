"""Pydantic models for namespace MCP actions."""

from enum import Enum

from pydantic import BaseModel, Field


class NamespaceStyle(str, Enum):
    """Output style options for namespace queries."""
    SHORT = "short"
    LONG = "long"
    DETAILS = "details"


class ScopeInfo(BaseModel):
    """Scope information in namespace responses."""
    description: str = Field(description="Scope description")


class NamespaceInfo(BaseModel):
    """Namespace information with scopes."""
    description: str = Field(description="Namespace description")
    scopes: dict[str, ScopeInfo] | None = Field(
        default=None,
        description="Scopes within namespace (style-dependent)"
    )


# =============================================================================
# get_namespaces
# =============================================================================

class GetNamespacesInput(BaseModel):
    """Input for get_namespaces MCP action."""
    namespace: str | None = Field(
        default=None,
        description="Optional exact match filter for specific namespace"
    )
    style: NamespaceStyle = Field(
        default=NamespaceStyle.SHORT,
        description="Output detail level"
    )


class GetNamespacesOutput(BaseModel):
    """Output for get_namespaces MCP action."""
    namespaces: dict[str, NamespaceInfo] = Field(
        description="Discovered namespaces with their scopes"
    )


# =============================================================================
# create_namespace
# =============================================================================

class CreateNamespaceInput(BaseModel):
    """Input for create_namespace MCP action."""
    name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9\-_]+$",
        description="Namespace name (lowercase, alphanumeric, hyphens, underscores)"
    )
    description: str = Field(
        min_length=1,
        max_length=500,
        description="Human-readable namespace description"
    )


class CreateNamespaceOutput(BaseModel):
    """Output for create_namespace MCP action."""
    name: str = Field(description="Created namespace name")
    description: str = Field(description="Namespace description")
    scopes: dict[str, ScopeInfo] = Field(
        description="Automatically created scopes (includes default)"
    )


# =============================================================================
# update_namespace
# =============================================================================

class UpdateNamespaceInput(BaseModel):
    """Input for update_namespace MCP action."""
    name: str = Field(
        min_length=1,
        description="Current namespace name"
    )
    new_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9\-_]+$",
        description="New namespace name (optional)"
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Updated namespace description (optional)"
    )


class UpdateNamespaceOutput(BaseModel):
    """Output for update_namespace MCP action."""
    name: str = Field(description="Updated namespace name")
    description: str = Field(description="Updated namespace description")
    scopes: dict[str, ScopeInfo] = Field(
        description="All scopes in the updated namespace"
    )


# =============================================================================
# delete_namespace
# =============================================================================

class DeleteNamespaceInput(BaseModel):
    """Input for delete_namespace MCP action."""
    name: str = Field(
        min_length=1,
        description="Namespace name to delete"
    )


class DeleteNamespaceOutput(BaseModel):
    """Output for delete_namespace MCP action."""
    name: str = Field(description="Deleted namespace name")
    scopes_count: int = Field(
        ge=0,
        description="Number of scopes deleted"
    )
    knowledge_count: int = Field(
        ge=0,
        description="Number of knowledge entries deleted"
    )
