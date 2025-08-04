"""Pydantic models for namespace MCP actions."""

from pydantic import BaseModel, Field

from ..types import NamespaceStyle


class NamespaceInfo(BaseModel):
    """Namespace information with metadata."""

    name: str = Field(description="Namespace name")
    description: str = Field(description="Namespace description")


class ScopeInfo(BaseModel):
    """Scope information with parent relationships."""

    name: str = Field(description="Scope name")
    namespace: str = Field(description="Parent namespace name")
    description: str = Field(description="Scope description")
    parents: list[str] = Field(default_factory=list, description="Parent scope names")


class GetNamespacesInput(BaseModel):
    """Input for get_namespaces MCP action."""

    namespace: str | None = Field(
        default=None, description="Optional exact match filter for specific namespace"
    )
    style: NamespaceStyle = Field(
        default=NamespaceStyle.SHORT, description="Output detail level"
    )


class ScopeData(BaseModel):
    """Scope data within namespace for spec compliance."""
    
    description: str = Field(description="Scope description")
    parents: list[str] | None = Field(default=None, description="Parent scope names (details style only)")


class NamespaceData(BaseModel):
    """Namespace data for spec compliance."""
    
    description: str = Field(description="Namespace description")
    scopes: dict[str, ScopeData] | None = Field(default=None, description="Nested scopes (long/details style only)")


class GetNamespacesOutput(BaseModel):
    """Output for get_namespaces MCP action matching specification structure."""

    namespaces: dict[str, NamespaceData] = Field(
        description="Dictionary of namespaces with nested structure per MCP specification"
    )


class CreateNamespaceInput(BaseModel):
    """Input for create_namespace MCP action."""

    name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9\-_]+$",
        description="Namespace name (lowercase, alphanumeric, hyphens, underscores)",
    )
    description: str = Field(
        min_length=1, max_length=500, description="Human-readable namespace description"
    )


class CreateNamespaceOutput(BaseModel):
    """Output for create_namespace MCP action."""

    name: str = Field(description="Created namespace name")
    description: str = Field(description="Namespace description")
    scopes: dict[str, ScopeData] = Field(
        description="Automatically created scopes (includes default)"
    )


class UpdateNamespaceInput(BaseModel):
    """Input for update_namespace MCP action."""

    name: str = Field(min_length=1, description="Current namespace name")
    new_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9\-_]+$",
        description="New namespace name (optional)",
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Updated namespace description (optional)",
    )


class UpdateNamespaceOutput(BaseModel):
    """Output for update_namespace MCP action."""

    name: str = Field(description="Updated namespace name")
    description: str = Field(description="Updated namespace description")
    scopes: dict[str, ScopeData] = Field(
        description="All scopes in the updated namespace"
    )


class DeleteNamespaceInput(BaseModel):
    """Input for delete_namespace MCP action."""

    name: str = Field(min_length=1, description="Namespace name to delete")


class DeleteNamespaceOutput(BaseModel):
    """Output for delete_namespace MCP action."""

    name: str = Field(description="Deleted namespace name")
    scopes_count: int = Field(ge=0, description="Number of scopes deleted")
    knowledge_count: int = Field(
        ge=0, description="Number of knowledge entries deleted"
    )
