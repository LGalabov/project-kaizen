"""Project Kaizen MCP Server - FastMCP server with all tools."""

from typing import Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from project_kaizen.models import (
    validate_knowledge,
    validate_namespace,
    validate_scope,
)


# Lazy import - database will be imported when first tool is called
def get_db() -> Any:
    """Lazy initialization of database module."""
    from project_kaizen import database

    return database


# Create the FastMCP server instance
mcp = FastMCP("project-kaizen")


# ============================================================================
# NAMESPACE TOOLS
# ============================================================================


@mcp.tool
async def get_namespaces(
    ctx: Context,
    namespace: str | None = Field(
        default=None, description="Optional exact match filter for specific namespace"
    ),
    style: Literal["short", "long", "details"] = Field(
        default="short", description="Output detail level: short, long, or details"
    ),
) -> dict[str, Any]:
    """Discover existing namespaces and scopes for organizational structure decisions."""
    await ctx.info(f"Getting namespaces with filter={namespace}, style={style}")

    try:
        if namespace:
            validate_namespace(namespace)

        result = await get_db().get_namespaces(namespace, style)

        await ctx.debug(f"Found {len(result.get('namespaces', {}))} namespaces")
        return result

    except Exception as e:
        await ctx.error(f"Failed to get namespaces: {str(e)}")
        raise


@mcp.tool
async def create_namespace(
    ctx: Context,
    namespace: str = Field(
        ..., description="Namespace name (lowercase, alphanumeric, hyphens, underscores)"
    ),
    description: str = Field(..., description="Human-readable namespace description"),
) -> dict[str, Any]:
    """Create new namespace with automatic 'default' scope for immediate knowledge storage."""
    await ctx.info(f"Creating namespace '{namespace}'")

    try:
        validate_namespace(namespace)

        result = await get_db().create_namespace(namespace, description)

        await ctx.info(f"Created namespace '{namespace}' with default scope")
        return result

    except Exception as e:
        await ctx.error(f"Failed to create namespace '{namespace}': {str(e)}")
        raise


@mcp.tool
async def update_namespace(
    ctx: Context,
    namespace: str = Field(..., description="Current namespace name"),
    new_namespace: str | None = Field(default=None, description="New namespace name (optional)"),
    new_description: str | None = Field(
        default=None, description="Updated namespace description (optional)"
    ),
) -> dict[str, Any]:
    """Update namespace name and/or description with automatic reference updating."""
    await ctx.info(f"Updating namespace '{namespace}'")

    try:
        # Validate that at least one update parameter is provided
        if not new_namespace and not new_description:
            raise ValueError("At least one of new_namespace or new_description must be provided")

        validate_namespace(namespace)
        if new_namespace:
            validate_namespace(new_namespace)

        result = await get_db().update_namespace(namespace, new_namespace, new_description)

        await ctx.info(
            f"Updated namespace '{namespace}'" + (f" to '{new_namespace}'" if new_namespace else "")
        )
        return result

    except Exception as e:
        await ctx.error(f"Failed to update namespace '{namespace}': {str(e)}")
        raise


@mcp.tool
async def delete_namespace(
    ctx: Context, namespace: str = Field(..., description="Namespace name to delete")
) -> dict[str, Any]:
    """Remove namespace and all associated scopes and knowledge entries."""
    await ctx.warning(f"Deleting namespace '{namespace}' and all its data")

    try:
        validate_namespace(namespace)

        result = await get_db().delete_namespace(namespace)

        await ctx.info(
            f"Deleted namespace '{namespace}' with {result.get('scopes_count', 0)} scopes "
            f"and {result.get('knowledge_count', 0)} knowledge entries"
        )
        return result

    except Exception as e:
        await ctx.error(f"Failed to delete namespace '{namespace}': {str(e)}")
        raise


# ============================================================================
# SCOPE TOOLS
# ============================================================================


@mcp.tool
async def create_scope(
    ctx: Context,
    scope: str = Field(..., description="Full scope identifier (namespace:scope_name)"),
    description: str = Field(..., description="Human-readable scope description"),
    parents: list[str] | None = Field(
        default=None, description="Optional parent scope identifiers"
    ),
) -> dict[str, Any]:
    """Create new scope within namespace with automatic 'default' parent inheritance."""
    await ctx.info(f"Creating scope '{scope}'")

    try:
        validate_scope(scope)
        if parents:
            for parent in parents:
                validate_scope(parent)

        result = await get_db().create_scope(scope, description, parents)

        await ctx.info(f"Created scope '{scope}' with {len(result.get('parents', []))} parents")
        return result

    except Exception as e:
        await ctx.error(f"Failed to create scope '{scope}': {str(e)}")
        raise


@mcp.tool
async def update_scope(
    ctx: Context,
    scope: str = Field(..., description="Current scope identifier (namespace:scope_name)"),
    new_scope: str | None = Field(default=None, description="New scope identifier (optional)"),
    new_description: str | None = Field(
        default=None, description="Updated scope description (optional)"
    ),
    new_parents: list[str] | None = Field(
        default=None, description="Updated parent scope identifiers (optional)"
    ),
) -> dict[str, Any]:
    """Update scope name, description, and parent relationships with auto-updates."""
    await ctx.info(f"Updating scope '{scope}'")

    try:
        # Validate that at least one update parameter is provided
        if not new_scope and not new_description and new_parents is None:
            raise ValueError(
                "At least one of new_scope, new_description, or new_parents must be provided"
            )

        validate_scope(scope)
        if new_scope:
            validate_scope(new_scope)
        if new_parents:
            for parent in new_parents:
                validate_scope(parent)

        result = await get_db().update_scope(scope, new_scope, new_description, new_parents)

        await ctx.info(f"Updated scope '{scope}'" + (f" to '{new_scope}'" if new_scope else ""))
        return result

    except Exception as e:
        await ctx.error(f"Failed to update scope '{scope}': {str(e)}")
        raise


@mcp.tool
async def delete_scope(
    ctx: Context,
    scope: str = Field(..., description="Scope identifier to delete (namespace:scope_name)"),
) -> dict[str, Any]:
    """Remove scope and all associated knowledge entries."""
    await ctx.warning(f"Deleting scope '{scope}' and all its knowledge")

    try:
        validate_scope(scope)

        result = await get_db().delete_scope(scope)

        await ctx.info(
            f"Deleted scope '{scope}' with {result.get('knowledge_deleted', 0)} knowledge entries"
        )
        return result

    except Exception as e:
        await ctx.error(f"Failed to delete scope '{scope}': {str(e)}")
        raise


# ============================================================================
# KNOWLEDGE TOOLS
# ============================================================================


@mcp.tool
async def write_knowledge(
    ctx: Context,
    scope: str = Field(..., description="Target scope identifier (namespace:scope_name)"),
    content: str = Field(..., description="Knowledge content to store"),
    context: str = Field(..., description="Context or summary for the knowledge entry"),
    task_size: Literal["XS", "S", "M", "L", "XL"] | None = Field(
        default=None, description="Task complexity: XS, S, M, L, or XL"
    ),
) -> dict[str, Any]:
    """Store new knowledge entry with automatic scope assignment and context tagging."""
    await ctx.info(f"Writing knowledge to scope '{scope}' (task_size: {task_size})")

    try:
        validate_scope(scope)
        validate_knowledge(content, context)

        result = await get_db().write_knowledge(scope, content, context, task_size)

        await ctx.info(f"Created knowledge entry {result.get('id')} in scope '{scope}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to write knowledge to '{scope}': {str(e)}")
        raise


@mcp.tool
async def update_knowledge(
    ctx: Context,
    id: str = Field(..., description="Knowledge entry ID to update"),
    content: str | None = Field(default=None, description="Updated knowledge content (optional)"),
    context: str | None = Field(default=None, description="Updated context or summary (optional)"),
    scope: str | None = Field(default=None, description="Updated scope identifier (optional)"),
    task_size: Literal["XS", "S", "M", "L", "XL"] | None = Field(
        default=None, description="Task complexity: XS, S, M, L, or XL"
    ),
) -> dict[str, Any]:
    """Update knowledge entry content, context, or scope assignment."""
    await ctx.info(f"Updating knowledge entry {id} (task_size: {task_size})")

    try:
        # Validate that at least one update parameter is provided
        if not content and not context and not scope and task_size is None:
            raise ValueError(
                "At least one of content, context, scope, or task_size must be provided"
            )

        if scope:
            validate_scope(scope)
        if content or context:
            # Validate both if at least one is provided
            validate_knowledge(content or "", context or "")

        result = await get_db().update_knowledge(id, content, context, scope, task_size)

        await ctx.info(f"Updated knowledge entry {id}")
        return result

    except Exception as e:
        await ctx.error(f"Failed to update knowledge {id}: {str(e)}")
        raise


@mcp.tool
async def delete_knowledge(
    ctx: Context, id: str = Field(..., description="Knowledge entry ID to delete")
) -> dict[str, Any]:
    """Remove knowledge entry from system."""
    await ctx.info(f"Deleting knowledge entry {id}")

    try:
        result = await get_db().delete_knowledge(id)

        await ctx.info(f"Deleted knowledge entry {id}")
        return result

    except Exception as e:
        await ctx.error(f"Failed to delete knowledge {id}: {str(e)}")
        raise


@mcp.tool
async def resolve_knowledge_conflict(
    ctx: Context,
    active_id: str = Field(..., description="Knowledge entry ID to keep as active"),
    suppressed_ids: list[str] = Field(
        ..., description="Knowledge entry IDs to suppress due to conflict"
    ),
) -> dict[str, Any]:
    """Mark knowledge entries for conflict resolution when contradictory information exists."""
    await ctx.info(
        f"Resolving conflict: keeping {active_id}, suppressing {len(suppressed_ids)} entries"
    )

    try:
        if not suppressed_ids:
            raise ValueError("suppressed_ids cannot be empty")

        result = await get_db().resolve_conflict(active_id, suppressed_ids)

        await ctx.info(
            f"Resolved conflict: {active_id} active, {len(suppressed_ids)} entries suppressed"
        )
        return result

    except Exception as e:
        await ctx.error(f"Failed to resolve conflict for {active_id}: {str(e)}")
        raise


@mcp.tool
async def get_task_context(
    ctx: Context,
    queries: list[str] = Field(..., description="Multiple targeted search queries for the task"),
    scope: str = Field(..., description="Scope to search within (namespace:scope_name)"),
    task_size: Literal["XS", "S", "M", "L", "XL"] | None = Field(
        default=None, description="Task complexity: XS, S, M, L, or XL"
    ),
) -> dict[str, Any]:
    """Search knowledge using multiple queries and return results by scope hierarchy."""
    await ctx.info(f"Searching with {len(queries)} queries in scope '{scope}'")

    try:
        if not queries:
            raise ValueError("queries cannot be empty")
        validate_scope(scope)

        result = await get_db().get_task_context(queries, scope, task_size)

        # Count total results
        total_results = sum(len(entries) for entries in result.values())
        await ctx.info(f"Found {total_results} knowledge entries across {len(result)} scopes")

        return result

    except Exception as e:
        await ctx.error(f"Failed to search knowledge: {str(e)}")
        raise
