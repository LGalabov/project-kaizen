"""Project Kaizen MCP Server - FastMCP server with all tools."""

from typing import Any

from fastmcp import Context, FastMCP
from pydantic import Field

from project_kaizen.validators import (
    validate_content,
    validate_context,
    validate_description,
    validate_namespace,
    validate_scope,
    validate_style,
    validate_task_size,
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
    namespace: str = Field(description="Filter by name • Optional • Text • Ex: 'shopcraft'"),
    style: str = Field(
        description="Detail level • Optional • Choice (short/long/details) • Ex: 'details'"
    ),
) -> dict[str, Any]:
    """Discover existing namespaces and scopes for organizational structure decisions."""
    await ctx.info(f"Getting namespaces with filter={namespace}, style={style}")

    validate_namespace(namespace)
    style = style or "short"
    validate_style(style)

    try:
        result = await get_db().get_namespaces(namespace, style)

        await ctx.debug(f"Found {len(result.get('namespaces', {}))} namespaces")
        return result

    except Exception as e:
        await ctx.error(f"Failed to get namespaces: {str(e)}")
        raise


@mcp.tool
async def create_namespace(
    ctx: Context,
    namespace: str = Field(description="Namespace name • Required • Text • Ex: 'shopcraft'"),
    description: str = Field(
        description="Description • Required • Text • Ex: 'E-commerce platform'"
    ),
) -> dict[str, Any]:
    """Create new namespace with automatic 'default' scope for immediate knowledge storage."""
    await ctx.info(f"Creating namespace '{namespace}'")

    validate_namespace(namespace)
    validate_description(description)

    try:
        result = await get_db().create_namespace(namespace, description)

        await ctx.info(f"Created namespace '{namespace}' with default scope")
        return result

    except Exception as e:
        await ctx.error(f"Failed to create namespace '{namespace}': {str(e)}")
        raise


@mcp.tool
async def update_namespace(
    ctx: Context,
    namespace: str = Field(description="Namespace to update • Required • Text • Ex: 'shopcraft'"),
    new_namespace: str = Field(description="New name • Optional • Text • Ex: 'shop-api'"),
    new_description: str = Field(
        description="New description • Optional • Text • Ex: 'Shop API services'"
    ),
) -> dict[str, Any]:
    """Update namespace name and/or description with automatic reference updating."""
    await ctx.info(f"Updating namespace '{namespace}'")

    validate_namespace(namespace)

    if not (new_namespace or new_description):
        raise ValueError("At least one of new_namespace or new_description must be provided")

    validate_namespace(new_namespace)
    validate_description(new_description)

    try:
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
    ctx: Context,
    namespace: str = Field(description="Namespace to delete • Required • Text • Ex: 'old-project'"),
) -> dict[str, Any]:
    """Remove namespace and all associated scopes and knowledge entries."""
    await ctx.warning(f"Deleting namespace '{namespace}' and all its data")

    validate_namespace(namespace)

    try:
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
    scope: str = Field(description="Scope identifier • Required • Text • Ex: 'shopcraft:backend'"),
    description: str = Field(
        description="Description • Required • Text • Ex: 'Backend API services'"
    ),
    parents: list[str] = Field(
        description="Parent scopes • Optional • List • Ex: ['shopcraft:default']"
    ),
) -> dict[str, Any]:
    """Create new scope within namespace with automatic 'default' parent inheritance."""
    await ctx.info(f"Creating scope '{scope}'")

    validate_scope(scope)
    validate_description(description)

    for parent in parents or []:
        validate_scope(parent)

    try:
        result = await get_db().create_scope(scope, description, parents)

        await ctx.info(f"Created scope '{scope}' with {len(result.get('parents', []))} parents")
        return result

    except Exception as e:
        await ctx.error(f"Failed to create scope '{scope}': {str(e)}")
        raise


@mcp.tool
async def update_scope(
    ctx: Context,
    scope: str = Field(description="Scope to update • Required • Text • Ex: 'shopcraft:backend'"),
    new_scope: str = Field(description="New scope name • Optional • Text • Ex: 'shopcraft:api'"),
    new_description: str = Field(
        description="Updated description • Optional • Text • Ex: 'API endpoints'"
    ),
    new_parents: list[str] = Field(
        description="Parent scopes • Optional • List • Ex: ['shopcraft:default', 'java:default']"
    ),
) -> dict[str, Any]:
    """Update scope name, description, and parent relationships with auto-updates."""
    await ctx.info(f"Updating scope '{scope}'")

    validate_scope(scope)

    if not (new_scope or new_description or new_parents):
        raise ValueError(
            "At least one of new_scope, new_description, or new_parents must be provided"
        )

    validate_scope(new_scope)
    validate_description(new_description)

    for parent in new_parents or []:
        validate_scope(parent)

    try:
        result = await get_db().update_scope(scope, new_scope, new_description, new_parents)

        await ctx.info(f"Updated scope '{scope}'" + (f" to '{new_scope}'" if new_scope else ""))
        return result

    except Exception as e:
        await ctx.error(f"Failed to update scope '{scope}': {str(e)}")
        raise


@mcp.tool
async def delete_scope(
    ctx: Context,
    scope: str = Field(description="Scope to delete • Required • Text • Ex: 'shopcraft:legacy'"),
) -> dict[str, Any]:
    """Remove scope and all associated knowledge entries."""
    await ctx.warning(f"Deleting scope '{scope}' and all its knowledge")

    validate_scope(scope)

    try:
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
    scope: str = Field(description="Target scope • Required • Text • Ex: 'shopcraft:backend'"),
    content: str = Field(
        description="Knowledge content • Required • Text • Ex: 'API uses REST patterns'"
    ),
    context: str = Field(
        description="Summary/context • Required • Text • Ex: 'Architecture decision'"
    ),
    task_size: str = Field(
        description="Task complexity • Optional • Choice (XS/S/M/L/XL) • Ex: 'M'"
    ),
) -> dict[str, Any]:
    """Store new knowledge entry with automatic scope assignment and context tagging."""
    await ctx.info(f"Writing knowledge to scope '{scope}' (task_size: {task_size})")

    validate_scope(scope)
    validate_content(content)
    validate_context(context)
    validate_task_size(task_size)

    try:
        result = await get_db().write_knowledge(scope, content, context, task_size)

        await ctx.info(f"Created knowledge entry {result.get('id')} in scope '{scope}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to write knowledge to '{scope}': {str(e)}")
        raise


@mcp.tool
async def update_knowledge(
    ctx: Context,
    knowledge_id: int = Field(description="Entry ID • Required • Number • Ex: 42"),
    content: str = Field(description="New content • Optional • Text • Ex: 'Updated API info'"),
    context: str = Field(description="New context • Optional • Text • Ex: 'Revised approach'"),
    scope: str = Field(description="New scope • Optional • Text • Ex: 'shopcraft:api'"),
    task_size: str = Field(
        description="Task complexity • Optional • Choice (XS/S/M/L/XL) • Ex: 'L'"
    ),
) -> dict[str, Any]:
    """Update knowledge entry content, context, or scope assignment."""
    await ctx.info(f"Updating knowledge entry {knowledge_id} (task_size: {task_size})")

    if not (content or context or scope or task_size):
        raise ValueError("At least one of content, context, scope, or task_size must be provided")

    validate_content(content)
    validate_context(context)
    validate_scope(scope)
    validate_task_size(task_size)

    try:
        result = await get_db().update_knowledge(knowledge_id, content, context, scope, task_size)

        await ctx.info(f"Updated knowledge entry {knowledge_id}")
        return result

    except Exception as e:
        await ctx.error(f"Failed to update knowledge {knowledge_id}: {str(e)}")
        raise


@mcp.tool
async def delete_knowledge(
    ctx: Context,
    knowledge_id: int = Field(description="Entry ID to delete • Required • Number • Ex: 42"),
) -> dict[str, Any]:
    """Remove knowledge entry from system."""
    await ctx.info(f"Deleting knowledge entry {knowledge_id}")

    try:
        result = await get_db().delete_knowledge(knowledge_id)

        await ctx.info(f"Deleted knowledge entry {knowledge_id}")
        return result

    except Exception as e:
        await ctx.error(f"Failed to delete knowledge {knowledge_id}: {str(e)}")
        raise


@mcp.tool
async def resolve_knowledge_conflict(
    ctx: Context,
    active_id: int = Field(description="ID to keep active • Required • Number • Ex: 42"),
    suppressed_ids: list[int] = Field(
        description="IDs to suppress • Required • List • Ex: [43, 44, 45]"
    ),
) -> dict[str, Any]:
    """Mark knowledge entries for conflict resolution when contradictory information exists."""
    await ctx.info(
        f"Resolving conflict: keeping {active_id}, suppressing {len(suppressed_ids)} entries"
    )

    if not suppressed_ids:
        raise ValueError("suppressed_ids cannot be empty")

    try:
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
    queries: list[str] = Field(
        description="Search queries • Required • List • Ex: ['REST API', 'authentication']"
    ),
    scope: str = Field(description="Search scope • Required • Text • Ex: 'shopcraft:backend'"),
    task_size: str = Field(
        description="Task complexity • Optional • Choice (XS/S/M/L/XL) • Ex: 'L'"
    ),
) -> dict[str, Any]:
    """Search knowledge using multiple queries and return results by scope hierarchy."""
    await ctx.info(f"Searching with {len(queries)} queries in scope '{scope}'")

    if not queries:
        raise ValueError("queries cannot be empty")

    validate_scope(scope)
    validate_task_size(task_size)

    try:
        result = await get_db().get_task_context(queries, scope, task_size)

        # Count total results
        total_results = sum(len(entries) for entries in result.values())
        await ctx.info(f"Found {total_results} knowledge entries across {len(result)} scopes")

        return result

    except Exception as e:
        await ctx.error(f"Failed to search knowledge: {str(e)}")
        raise
