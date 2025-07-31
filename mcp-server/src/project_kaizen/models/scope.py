"""Pydantic models for scope MCP actions."""

from pydantic import BaseModel, Field, field_validator


def validate_scope_format(scope: str) -> str:
    """Validate scope follows namespace:scope format."""
    if ":" not in scope:
        raise ValueError("Scope must follow 'namespace:scope' format")

    namespace, scope_name = scope.split(":", 1)

    if not namespace or not scope_name:
        raise ValueError("Both namespace and scope parts must be non-empty")

    # Validate namespace format
    if not namespace.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Namespace must contain only alphanumeric, hyphens, underscores")

    # Validate scope name format
    if not scope_name.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Scope name must contain only alphanumeric, hyphens, underscores")

    return scope


# =============================================================================
# create_scope
# =============================================================================

class CreateScopeInput(BaseModel):
    """Input for create_scope MCP action."""
    scope: str = Field(
        min_length=3,  # minimum: "a:b"
        max_length=200,
        description="Scope identifier in 'namespace:scope' format"
    )
    description: str = Field(
        min_length=1,
        max_length=500,
        description="Human-readable scope description"
    )
    parents: list[str] = Field(
        default_factory=list,
        description="Parent scope identifiers (namespace:default auto-added)"
    )

    @field_validator("scope")
    @classmethod
    def validate_scope_format_field(cls, v: str) -> str:
        """Validate scope format."""
        return validate_scope_format(v)

    @field_validator("parents")
    @classmethod
    def validate_parent_scopes(cls, v: list[str]) -> list[str]:
        """Validate all parent scopes follow correct format."""
        return [validate_scope_format(parent) for parent in v]


class CreateScopeOutput(BaseModel):
    """Output for create_scope MCP action."""
    scope: str = Field(description="Created scope identifier")
    description: str = Field(description="Scope description")
    parents: list[str] = Field(
        description="All parent scopes (including auto-added namespace:default)"
    )


# =============================================================================
# update_scope
# =============================================================================

class UpdateScopeInput(BaseModel):
    """Input for update_scope MCP action."""
    scope: str = Field(
        min_length=3,
        description="Current scope identifier in 'namespace:scope' format"
    )
    new_scope: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
        description="New scope identifier (optional)"
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Updated scope description (optional)"
    )
    parents: list[str] | None = Field(
        default=None,
        description="Updated parent scope list (namespace:default always preserved)"
    )

    @field_validator("scope")
    @classmethod
    def validate_current_scope(cls, v: str) -> str:
        """Validate current scope format."""
        return validate_scope_format(v)

    @field_validator("new_scope")
    @classmethod
    def validate_new_scope_format(cls, v: str | None) -> str | None:
        """Validate new scope format if provided."""
        return validate_scope_format(v) if v is not None else None

    @field_validator("parents")
    @classmethod
    def validate_parent_list(cls, v: list[str] | None) -> list[str] | None:
        """Validate parent scope formats if provided."""
        return [validate_scope_format(parent) for parent in v] if v is not None else None


class UpdateScopeOutput(BaseModel):
    """Output for update_scope MCP action."""
    scope: str = Field(description="Updated scope identifier")
    description: str = Field(description="Updated scope description")
    parents: list[str] = Field(
        description="All parent scopes (namespace:default always preserved)"
    )


# =============================================================================
# delete_scope
# =============================================================================

class DeleteScopeInput(BaseModel):
    """Input for delete_scope MCP action."""
    scope: str = Field(
        min_length=3,
        description="Scope identifier to delete in 'namespace:scope' format"
    )

    @field_validator("scope")
    @classmethod
    def validate_scope_to_delete(cls, v: str) -> str:
        """Validate scope format and prevent default scope deletion."""
        validated_scope = validate_scope_format(v)

        # Prevent deletion of default scopes
        if validated_scope.endswith(":default"):
            raise ValueError("Cannot delete default scope")

        return validated_scope


class DeleteScopeOutput(BaseModel):
    """Output for delete_scope MCP action."""
    scope: str = Field(description="Deleted scope identifier")
    knowledge_deleted: int = Field(
        ge=0,
        description="Number of knowledge entries deleted"
    )
