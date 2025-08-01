"""Pydantic models for knowledge MCP actions."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from .scope import validate_scope_format


class TaskSize(str, Enum):
    """Task complexity levels for knowledge filtering."""

    XS = "XS"  # Quick fixes
    S = "S"  # Small features
    M = "M"  # Medium projects
    L = "L"  # Large implementations
    XL = "XL"  # Architectural changes


def validate_knowledge_id(knowledge_id: str) -> str:
    """Validate knowledge ID format."""
    if not knowledge_id or len(knowledge_id) < 8:
        raise ValueError("Knowledge ID must be at least 8 characters")

    if not knowledge_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError(
            "Knowledge ID must contain only alphanumeric, hyphens, underscores"
        )

    return knowledge_id


# =============================================================================
# write_knowledge
# =============================================================================


class WriteKnowledgeInput(BaseModel):
    """Input for write_knowledge MCP action."""

    content: str = Field(
        min_length=10, max_length=50000, description="Knowledge entry content"
    )
    context: str = Field(
        min_length=5, max_length=1000, description="Context keywords for searchability"
    )
    scope: str = Field(
        min_length=3, description="Scope identifier in 'namespace:scope' format"
    )

    @field_validator("scope")
    @classmethod
    def validate_scope_format_field(cls, v: str) -> str:
        """Validate scope format."""
        return validate_scope_format(v)


class WriteKnowledgeOutput(BaseModel):
    """Output for write_knowledge MCP action."""

    id: str = Field(description="Generated knowledge entry ID")
    scope: str = Field(description="Assigned scope identifier")


# =============================================================================
# update_knowledge
# =============================================================================


class UpdateKnowledgeInput(BaseModel):
    """Input for update_knowledge MCP action."""

    id: str = Field(min_length=8, description="Knowledge entry ID to update")
    content: str | None = Field(
        default=None,
        min_length=10,
        max_length=50000,
        description="Updated knowledge content (optional)",
    )
    context: str | None = Field(
        default=None,
        min_length=5,
        max_length=1000,
        description="Updated context keywords (optional)",
    )
    scope: str | None = Field(
        default=None, min_length=3, description="Updated scope identifier (optional)"
    )

    @field_validator("id")
    @classmethod
    def validate_knowledge_id_field(cls, v: str) -> str:
        """Validate knowledge ID format."""
        return validate_knowledge_id(v)

    @field_validator("scope")
    @classmethod
    def validate_scope_format_field(cls, v: str | None) -> str | None:
        """Validate scope format if provided."""
        return validate_scope_format(v) if v is not None else None


class UpdateKnowledgeOutput(BaseModel):
    """Output for update_knowledge MCP action."""

    id: str = Field(description="Updated knowledge entry ID")
    scope: str = Field(description="Current scope identifier")


# =============================================================================
# delete_knowledge
# =============================================================================


class DeleteKnowledgeInput(BaseModel):
    """Input for delete_knowledge MCP action."""

    id: str = Field(min_length=8, description="Knowledge entry ID to delete")

    @field_validator("id")
    @classmethod
    def validate_knowledge_id_field(cls, v: str) -> str:
        """Validate knowledge ID format."""
        return validate_knowledge_id(v)


class DeleteKnowledgeOutput(BaseModel):
    """Output for delete_knowledge MCP action."""

    id: str = Field(description="Deleted knowledge entry ID")


# =============================================================================
# resolve_knowledge_conflict
# =============================================================================


class ResolveKnowledgeConflictInput(BaseModel):
    """Input for resolve_knowledge_conflict MCP action."""

    active_id: str = Field(
        min_length=8, description="Knowledge entry ID to keep active"
    )
    suppressed_ids: list[str] = Field(
        min_length=1, description="Knowledge entry IDs to suppress"
    )

    @field_validator("active_id")
    @classmethod
    def validate_active_id(cls, v: str) -> str:
        """Validate active knowledge ID format."""
        return validate_knowledge_id(v)

    @field_validator("suppressed_ids")
    @classmethod
    def validate_suppressed_ids(cls, v: list[str]) -> list[str]:
        """Validate all suppressed knowledge IDs."""
        return [validate_knowledge_id(knowledge_id) for knowledge_id in v]


class ResolveKnowledgeConflictOutput(BaseModel):
    """Output for resolve_knowledge_conflict MCP action."""

    active_id: str = Field(description="Active knowledge entry ID")
    suppressed_ids: list[str] = Field(description="Suppressed knowledge entry IDs")


# =============================================================================
# get_task_context
# =============================================================================


class GetTaskContextInput(BaseModel):
    """Input for get_task_context MCP action."""

    queries: list[str] = Field(
        min_length=1,
        max_length=10,
        description="Multiple targeted queries for complex tasks",
    )
    scope: str = Field(
        min_length=3, description="Starting scope for knowledge search with inheritance"
    )
    task_size: TaskSize | None = Field(
        default=None, description="Task complexity filter (optional)"
    )

    @field_validator("queries")
    @classmethod
    def validate_queries(cls, v: list[str]) -> list[str]:
        """Validate query strings."""
        validated: list[str] = []
        for query in v:
            stripped_query = query.strip()
            if not stripped_query:
                raise ValueError("Query cannot be empty")
            if len(stripped_query) < 3:
                raise ValueError("Query must be at least 3 characters")
            if len(stripped_query) > 200:
                raise ValueError("Query cannot exceed 200 characters")
            validated.append(stripped_query)
        return validated

    @field_validator("scope")
    @classmethod
    def validate_scope_format_field(cls, v: str) -> str:
        """Validate scope format."""
        return validate_scope_format(v)


class GetTaskContextOutput(BaseModel):
    """Output for get_task_context MCP action."""

    results: dict[str, dict[str, str]] = Field(
        description="Knowledge organized by scope hierarchy (scope -> {id: content})"
    )
