"""Project Kaizen MCP Server."""

from typing import Any

from fastmcp import Context, FastMCP
from pydantic import Field

from . import database
from .validators import (
    validate_canonical_scope_name,
    validate_content,
    validate_context,
    validate_description,
    validate_namespace_name,
    validate_scope_name,
    validate_task_size,
)

mcp = FastMCP("project-kaizen")


# ============================================================================
# NAMESPACE TOOLS - Atomic operations for namespace management
# ============================================================================


@mcp.tool
async def list_namespaces(ctx: Context) -> dict[str, Any]:
    """List all namespaces with their scopes and parent relationships.

    Returns complete namespace information including all scopes and their parent
    relationships. This gives a full view of the organizational structure.

    Returns:
        Dictionary with namespaces, each containing description, scopes, and parent relationships
    """
    await ctx.info("Listing all namespaces with full details")

    try:
        result = await database.list_namespaces()

        await ctx.debug(f"Found {len(result.get('namespaces', {}))} namespaces")
        return result

    except Exception as e:
        await ctx.error(f"Failed to list namespaces: {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def get_namespace_details(
    ctx: Context,
    namespace_name: str = Field(description="Namespace name (2-64 chars, lowercase letters/numbers/-)"),
) -> dict[str, Any]:
    """Get complete details for a specific namespace including all scopes and parent relationships.

    Args:
        namespace_name: Namespace name

    Returns:
        Dictionary with namespace details, scopes, and parent relationships
    """
    await ctx.info(f"Getting details for namespace '{namespace_name}'")

    validate_namespace_name(namespace_name)

    try:
        result = await database.get_namespace_details(namespace_name)

        await ctx.debug(f"Retrieved namespace '{namespace_name}' with full details")
        return result

    except Exception as e:
        await ctx.error(f"Failed to get namespace details '{namespace_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def create_namespace(
    ctx: Context,
    namespace_name: str = Field(description="Unique namespace name (2-64 chars, lowercase letters/numbers/-)"),
    description: str = Field(description="Namespace purpose (2-64 chars, free text, cannot be just whitespace)"),
) -> dict[str, Any]:
    """Create new namespace with automatic default scope.

    Creates a new organizational namespace. A 'default' scope is automatically
    created within the namespace for immediate knowledge storage.

    Args:
        namespace_name: Unique namespace name
        description: Clear description of namespace purpose

    Returns:
        Dictionary with created namespace and auto-created default scope
    """
    await ctx.info(f"Creating namespace '{namespace_name}'")

    validate_namespace_name(namespace_name)
    validate_description(description)

    try:
        result = await database.create_namespace(namespace_name, description)

        await ctx.info(f"Created namespace '{namespace_name}' with default scope")
        return result

    except Exception as e:
        await ctx.error(f"Failed to create namespace '{namespace_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def rename_namespace(
    ctx: Context,
    old_namespace_name: str = Field(description="Current namespace name (2-64 chars, lowercase letters/numbers/-)"),
    new_namespace_name: str = Field(description="New namespace name (2-64 chars, lowercase letters/numbers/-)"),
) -> dict[str, Any]:
    """Rename a namespace (all references auto-updated).

    Changes the name of an existing namespace. All scope references and
    knowledge entries are automatically updated to use the new name.

    Args:
        old_namespace_name: Current namespace name
        new_namespace_name: New namespace name

    Returns:
        Dictionary with updated namespace information
    """
    await ctx.info(f"Renaming namespace '{old_namespace_name}' to '{new_namespace_name}'")

    validate_namespace_name(old_namespace_name)
    validate_namespace_name(new_namespace_name)

    try:
        result = await database.rename_namespace(old_namespace_name, new_namespace_name)

        await ctx.info(f"Renamed namespace '{old_namespace_name}' to '{new_namespace_name}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to rename namespace '{old_namespace_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def update_namespace_description(
    ctx: Context,
    namespace_name: str = Field(description="Namespace to update (2-64 chars, lowercase letters/numbers/-)"),
    new_description: str = Field(description="New description (2-64 chars, free text, cannot be just whitespace)"),
) -> dict[str, Any]:
    """Update namespace description only.

    Changes the description of a namespace without affecting its name or structure.

    Args:
        namespace_name: Namespace to update
        new_description: New description

    Returns:
        Dictionary with updated namespace information
    """
    await ctx.info(f"Updating description for namespace '{namespace_name}'")

    validate_namespace_name(namespace_name)
    validate_description(new_description)

    try:
        result = await database.update_namespace_description(namespace_name, new_description)

        await ctx.info(f"Updated description for namespace '{namespace_name}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to update namespace description '{namespace_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def delete_namespace(
    ctx: Context,
    namespace_name: str = Field(description="Namespace to delete (2-64 chars, lowercase letters/numbers/-)"),
) -> dict[str, Any]:
    """Delete namespace and ALL associated data (cannot be undone).

    Permanently removes a namespace including all its scopes and knowledge entries.
    This is a destructive operation that cannot be reversed.

    Args:
        namespace_name: Namespace to delete permanently

    Returns:
        Dictionary with deletion statistics (scopes and knowledge entries removed)
    """
    await ctx.warning(f"Deleting namespace '{namespace_name}' and all its data")

    validate_namespace_name(namespace_name)

    try:
        result = await database.delete_namespace(namespace_name)

        await ctx.info(
            f"Deleted namespace '{namespace_name}' with {result.get('scopes_count', 0)} scopes "
            f"and {result.get('knowledge_count', 0)} knowledge entries"
        )
        
        # Return with expected keys for tests
        return {
            "namespace": namespace_name,
            "deleted_scopes": result.get("scopes_count", 0),
            "deleted_knowledge": result.get("knowledge_count", 0),
        }

    except Exception as e:
        await ctx.error(f"Failed to delete namespace '{namespace_name}': {str(e)}")
        raise


# ============================================================================
# SCOPE TOOLS - Atomic operations for scope management
# ============================================================================


# noinspection PyIncorrectDocstring
@mcp.tool
async def create_scope(
    ctx: Context,
    canonical_scope_name: str = Field(
        description="Full scope identifier 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
    description: str = Field(description="Purpose of this scope (2-64 chars, free text, cannot be just whitespace)"),
    parents: list[str] = Field(  # noqa: B008
        description=(
            "Parent canonical scope names like ['namespace:parent1'] (empty list = inherit from namespace:default only)"
        )
    ),
) -> dict[str, Any]:
    """Create a new scope with specified parent relationships.

    Creates a scope within a namespace. If the parent list is empty, the scope
    automatically inherits from the namespace's default scope.

    Args:
        canonical_scope_name: Full scope identifier
        description: Clear description of scope purpose
        parents: List of parent canonical scope names

    Returns:
        Dictionary with created scope and its parent relationships
    """
    await ctx.info(f"Creating scope '{canonical_scope_name}'")

    validate_canonical_scope_name(canonical_scope_name)
    validate_description(description)

    for parent in parents:
        validate_canonical_scope_name(parent)

    try:
        result = await database.create_scope(canonical_scope_name, description, parents)

        await ctx.info(f"Created scope '{canonical_scope_name}' with {len(parents)} explicit parents")
        return result

    except Exception as e:
        await ctx.error(f"Failed to create scope '{canonical_scope_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def rename_scope(
    ctx: Context,
    canonical_scope_name: str = Field(
        description=(
            "Full scope identifier to rename 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
        )
    ),
    new_scope_name: str = Field(
        description="New scope name only (2-64 chars, lowercase letters/numbers/-), stays in same namespace"
    ),
) -> dict[str, Any]:
    """Rename a scope within the same namespace (references auto-updated).

    Changes the name of a scope while keeping it in the same namespace.
    All knowledge entries and references are automatically updated.

    Args:
        canonical_scope_name: Full identifier of scope to rename
        new_scope_name: New scope name (namespace part stays the same)

    Returns:
        Dictionary with updated scope information
    """
    await ctx.info(f"Renaming scope '{canonical_scope_name}' with new name '{new_scope_name}'")

    validate_canonical_scope_name(canonical_scope_name)
    validate_scope_name(new_scope_name)

    try:
        result = await database.rename_scope(canonical_scope_name, new_scope_name)

        await ctx.info(f"Renamed scope '{canonical_scope_name}' to new name '{new_scope_name}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to rename scope '{canonical_scope_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def update_scope_description(
    ctx: Context,
    canonical_scope_name: str = Field(
        description="Full scope identifier 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
    new_description: str = Field(description="New description (2-64 chars, free text, cannot be just whitespace)"),
) -> dict[str, Any]:
    """Update scope description only.

    Changes the description of a scope without affecting its relationships or name.

    Args:
        canonical_scope_name: Full scope identifier to update
        new_description: New description

    Returns:
        Dictionary with updated scope information
    """
    await ctx.info(f"Updating description for scope '{canonical_scope_name}'")

    validate_canonical_scope_name(canonical_scope_name)
    validate_description(new_description)

    try:
        result = await database.update_scope_description(canonical_scope_name, new_description)

        await ctx.info(f"Updated description for scope '{canonical_scope_name}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to update scope description '{canonical_scope_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def add_scope_parent(
    ctx: Context,
    canonical_scope_name: str = Field(
        description="Full scope identifier 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
    parent_canonical_scope_name: str = Field(
        description="Parent scope to add 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
) -> dict[str, Any]:
    """Add a parent relationship to an existing scope.

    Adds a new parent scope for inheritance. The scope will inherit knowledge
    from this parent in addition to its existing parents.

    Args:
        canonical_scope_name: Full scope identifier to modify
        parent_canonical_scope_name: Full parent scope identifier to add

    Returns:
        Dictionary with updated scope and all parent relationships
    """
    await ctx.info(f"Adding parent '{parent_canonical_scope_name}' to scope '{canonical_scope_name}'")

    validate_canonical_scope_name(canonical_scope_name)
    validate_canonical_scope_name(parent_canonical_scope_name)

    try:
        result = await database.add_scope_parent(canonical_scope_name, parent_canonical_scope_name)

        await ctx.info(f"Added parent '{parent_canonical_scope_name}' to scope '{canonical_scope_name}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to add parent to scope '{canonical_scope_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def remove_scope_parent(
    ctx: Context,
    canonical_scope_name: str = Field(
        description="Full scope identifier 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
    parent_canonical_scope_name: str = Field(
        description="Parent scope to remove 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
) -> dict[str, Any]:
    """Remove a parent relationship from a scope.

    Removes an existing parent scope relationship. The scope will no longer
    inherit knowledge from this parent.

    Args:
        canonical_scope_name: Full scope identifier to modify
        parent_canonical_scope_name: Full parent scope identifier to remove

    Returns:
        Dictionary with updated scope and remaining parent relationships
    """
    await ctx.info(f"Removing parent '{parent_canonical_scope_name}' from scope '{canonical_scope_name}'")

    validate_canonical_scope_name(canonical_scope_name)
    validate_canonical_scope_name(parent_canonical_scope_name)

    try:
        result = await database.remove_scope_parent(canonical_scope_name, parent_canonical_scope_name)

        await ctx.info(f"Removed parent '{parent_canonical_scope_name}' from scope '{canonical_scope_name}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to remove parent from scope '{canonical_scope_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def delete_scope(
    ctx: Context,
    canonical_scope_name: str = Field(
        description=(
            "Full scope identifier to delete 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
        )
    ),
) -> dict[str, Any]:
    """Delete scope and ALL associated knowledge (cannot delete default scopes).

    Permanently removes a scope and all its knowledge entries. Default scopes
    cannot be deleted as they are required for namespace operation.

    Args:
        canonical_scope_name: Full scope identifier to delete permanently

    Returns:
        Dictionary with deletion statistics (knowledge entries removed)
    """
    await ctx.warning(f"Deleting scope '{canonical_scope_name}' and all its knowledge")

    validate_canonical_scope_name(canonical_scope_name)

    try:
        result = await database.delete_scope(canonical_scope_name)

        await ctx.info(
            f"Deleted scope '{canonical_scope_name}' with {result.get('knowledge_deleted', 0)} knowledge entries"
        )
        return result

    except Exception as e:
        await ctx.error(f"Failed to delete scope '{canonical_scope_name}': {str(e)}")
        raise


# ============================================================================
# KNOWLEDGE MANAGEMENT TOOLS - CRUD operations for knowledge entries
# ============================================================================


# noinspection PyIncorrectDocstring
@mcp.tool
async def write_knowledge(
    ctx: Context,
    canonical_scope_name: str = Field(
        description="Target scope 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
    content: str = Field(description="Knowledge content (non-empty, free text)"),
    context: str = Field(description="Summary/context of the knowledge (2-64 chars, free text)"),
    task_size: str | None = Field(default=None, description="Task complexity (XS/S/M/L/XL), null if not classified"),
) -> dict[str, Any]:
    """Store new knowledge entry with optional task size classification.

    Creates a new knowledge entry within the specified scope. Task size can be
    provided to classify the complexity of the knowledge for later filtering.

    Args:
        canonical_scope_name: Target scope for the knowledge
        content: The actual knowledge content
        context: Brief summary or context
        task_size: Optional complexity classification

    Returns:
        Dictionary with created knowledge entry ID and scope
    """
    await ctx.info(f"Writing knowledge to scope '{canonical_scope_name}' (task_size: {task_size})")

    validate_canonical_scope_name(canonical_scope_name)
    validate_content(content)
    validate_context(context)
    if task_size is not None:
        validate_task_size(task_size)

    try:
        result = await database.write_knowledge(canonical_scope_name, content, context, task_size)

        await ctx.info(f"Created knowledge entry {result.get('id')} in scope '{canonical_scope_name}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to write knowledge to '{canonical_scope_name}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def update_knowledge_content(
    ctx: Context,
    knowledge_id: int = Field(description="Knowledge entry ID to update"),
    new_content: str = Field(description="New knowledge content (non-empty, free text)"),
) -> dict[str, Any]:
    """Update the content of an existing knowledge entry.

    Modifies only the content of a knowledge entry, preserving all other attributes.

    Args:
        knowledge_id: ID of the knowledge entry to update
        new_content: New content to replace the existing content

    Returns:
        Dictionary with updated knowledge entry information
    """
    await ctx.info(f"Updating content for knowledge entry {knowledge_id}")

    validate_content(new_content)

    try:
        result = await database.update_knowledge_content(knowledge_id, new_content)

        await ctx.info(f"Updated content for knowledge entry {knowledge_id}")
        return result

    except Exception as e:
        await ctx.error(f"Failed to update knowledge content {knowledge_id}: {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def update_knowledge_context(
    ctx: Context,
    knowledge_id: int = Field(description="Knowledge entry ID to update"),
    new_context: str = Field(description="New context/summary (2-64 chars, free text)"),
) -> dict[str, Any]:
    """Update the context/summary of a knowledge entry.

    Modifies only the context of a knowledge entry, preserving all other attributes.

    Args:
        knowledge_id: ID of the knowledge entry to update
        new_context: New context or summary

    Returns:
        Dictionary with updated knowledge entry information
    """
    await ctx.info(f"Updating context for knowledge entry {knowledge_id}")

    validate_context(new_context)

    try:
        result = await database.update_knowledge_context(knowledge_id, new_context)

        await ctx.info(f"Updated context for knowledge entry {knowledge_id}")
        return result

    except Exception as e:
        await ctx.error(f"Failed to update knowledge context {knowledge_id}: {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def move_knowledge_to_scope(
    ctx: Context,
    knowledge_id: int = Field(description="Knowledge entry ID to move"),
    new_canonical_scope_name: str = Field(
        description="Target scope 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
) -> dict[str, Any]:
    """Move knowledge entry to a different scope.

    Relocates a knowledge entry from its current scope to a new scope.

    Args:
        knowledge_id: ID of the knowledge entry to move
        new_canonical_scope_name: Target scope for the knowledge

    Returns:
        Dictionary with updated knowledge entry information
    """
    await ctx.info(f"Moving knowledge entry {knowledge_id} to scope '{new_canonical_scope_name}'")

    validate_canonical_scope_name(new_canonical_scope_name)

    try:
        result = await database.move_knowledge_to_scope(knowledge_id, new_canonical_scope_name)

        await ctx.info(f"Moved knowledge entry {knowledge_id} to scope '{new_canonical_scope_name}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to move knowledge {knowledge_id}: {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def update_knowledge_task_size(
    ctx: Context,
    knowledge_id: int = Field(description="Knowledge entry ID to update"),
    new_task_size: str = Field(description="New task complexity (XS/S/M/L/XL)"),
) -> dict[str, Any]:
    """Update task size classification for a knowledge entry.

    Modifies only the task size of a knowledge entry, preserving all other attributes.

    Args:
        knowledge_id: ID of the knowledge entry to update
        new_task_size: New task complexity classification

    Returns:
        Dictionary with updated knowledge entry information
    """
    await ctx.info(f"Updating task size for knowledge entry {knowledge_id} to '{new_task_size}'")

    validate_task_size(new_task_size)

    try:
        result = await database.update_knowledge_task_size(knowledge_id, new_task_size)

        await ctx.info(f"Updated task size for knowledge entry {knowledge_id} to '{new_task_size}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to update knowledge task size {knowledge_id}: {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def delete_knowledge(
    ctx: Context,
    knowledge_id: int = Field(description="Knowledge entry ID to delete permanently"),
) -> dict[str, Any]:
    """Remove knowledge entry from the system (cannot be undone).

    Permanently deletes a knowledge entry from the database.

    Args:
        knowledge_id: ID of the knowledge entry to delete

    Returns:
        Dictionary confirming deletion with the deleted ID
    """
    await ctx.info(f"Deleting knowledge entry {knowledge_id}")

    try:
        result = await database.delete_knowledge(knowledge_id)

        await ctx.info(f"Deleted knowledge entry {knowledge_id}")
        return result

    except Exception as e:
        await ctx.error(f"Failed to delete knowledge {knowledge_id}: {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def resolve_knowledge_conflict(
    ctx: Context,
    active_knowledge_id: int = Field(description="Knowledge ID to keep as active/authoritative"),
    suppressed_knowledge_ids: list[int] = Field(description="Knowledge IDs to mark as superseded"),  # noqa: B008
) -> dict[str, Any]:
    """Mark knowledge entries for conflict resolution when contradictory information exists.

    When multiple knowledge entries contain conflicting information, this tool marks
    one as authoritative and others as superseded.

    Args:
        active_knowledge_id: The ID to keep as the authoritative version
        suppressed_knowledge_ids: IDs to mark as superseded

    Returns:
        Dictionary with conflict resolution details
    """
    await ctx.info(
        f"Resolving conflict: keeping {active_knowledge_id}, suppressing {len(suppressed_knowledge_ids)} entries"
    )

    if not suppressed_knowledge_ids:
        raise ValueError("suppressed_knowledge_ids cannot be empty")

    try:
        result = await database.resolve_knowledge_conflict(active_knowledge_id, suppressed_knowledge_ids)

        await ctx.info(
            f"Resolved conflict: {active_knowledge_id} active, {len(suppressed_knowledge_ids)} entries suppressed"
        )
        return result

    except Exception as e:
        await ctx.error(f"Failed to resolve conflict for {active_knowledge_id}: {str(e)}")
        raise


# ============================================================================
# KNOWLEDGE DISCOVERY TOOLS - Search and retrieval operations
# ============================================================================


# noinspection PyIncorrectDocstring
@mcp.tool
async def list_config(ctx: Context) -> dict[str, Any]:
    """List all configuration settings with their current and default values.

    Returns all system configuration parameters that control search behavior
    and other system operations. Shows both current and default values.

    Returns:
        Dictionary with all config keys and their values, defaults, types, and descriptions
    """
    await ctx.info("Listing all configuration settings")

    try:
        result = await database.list_config()

        await ctx.debug(f"Retrieved {len(result.get('configs', {}))} configuration settings")
        return result

    except Exception as e:
        await ctx.error(f"Failed to list configuration: {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def update_config(
    ctx: Context,
    key: str = Field(description="Configuration key to update (e.g., 'search.max_results')"),
    value: str = Field(description="New value for the configuration (will be validated)"),
) -> dict[str, Any]:
    """Update a configuration value.

    Updates a system configuration parameter. The value will be validated
    against the expected type before being applied.

    Args:
        key: Configuration key to update
        value: New value (will be validated against the type)

    Returns:
        Dictionary with the old value and new value
    """
    await ctx.info(f"Updating configuration '{key}' to '{value}'")

    if not key:
        raise ValueError("Configuration key cannot be empty")
    if value is None:
        raise ValueError("Configuration value cannot be null")

    try:
        result = await database.update_config(key, value)

        await ctx.info(f"Updated configuration '{key}' from '{result.get('old_value')}' to '{result.get('new_value')}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to update configuration '{key}': {str(e)}")
        raise


# noinspection PyIncorrectDocstring
@mcp.tool
async def reset_config(
    ctx: Context, key: str = Field(description="Configuration key to reset to default (e.g., 'search.max_results')")
) -> dict[str, Any]:
    """Reset a configuration value to its default.

    Resets a system configuration parameter back to its original default value.
    Useful for recovering from misconfigurations.

    Args:
        key: Configuration key to reset

    Returns:
        Dictionary with the reset value
    """
    await ctx.info(f"Resetting configuration '{key}' to default")

    if not key:
        raise ValueError("Configuration key cannot be empty")

    try:
        result = await database.reset_config(key)

        await ctx.info(f"Reset configuration '{key}' to default value '{result.get('value')}'")
        return result

    except Exception as e:
        await ctx.error(f"Failed to reset configuration '{key}': {str(e)}")
        raise


# ============================================================================
# KNOWLEDGE DISCOVERY TOOLS - Search and retrieval operations
# ============================================================================


# noinspection PyIncorrectDocstring
@mcp.tool
async def search_knowledge_base(
    ctx: Context,
    queries: list[str] = Field(description="Search terms like ['REST API', 'authentication']"),  # noqa: B008
    canonical_scope_name: str = Field(
        description="Search scope 'namespace:scope' (each part 2-64 chars, lowercase letters/numbers/-)"
    ),
    task_size: str | None = Field(
        default=None,
        description="Filter by task complexity (XS/S/M/L/XL), omit to include all sizes",
    ),
) -> dict[str, Any]:
    """Search knowledge base using multiple queries within the scope hierarchy.

    Searches for knowledge entries matching the provided queries within the specified
    scope and its hierarchy. Can optionally filter by task size.

    Args:
        queries: List of search terms to match
        canonical_scope_name: Scope to search within (includes hierarchy)
        task_size: Optional filter by task complexity

    Returns:
        Dictionary with search results organized by scope
    """
    await ctx.info(f"Searching with {len(queries)} queries in scope '{canonical_scope_name}'")

    if not queries:
        raise ValueError("queries cannot be empty")

    validate_canonical_scope_name(canonical_scope_name)
    if task_size is not None:
        validate_task_size(task_size)

    try:
        result = await database.search_knowledge_base(queries, canonical_scope_name, task_size)

        # Count total results
        total_results = sum(len(entries) for entries in result.values())
        await ctx.info(f"Found {total_results} knowledge entries across {len(result)} scopes")

        return result

    except Exception as e:
        await ctx.error(f"Failed to search knowledge: {str(e)}")
        raise
