"""MCP tools for scope management operations."""


from mcp.server.fastmcp import FastMCP

from ..database import db_manager
from ..models.scope import (
    CreateScopeInput,
    CreateScopeOutput,
    DeleteScopeInput,
    DeleteScopeOutput,
    UpdateScopeInput,
    UpdateScopeOutput,
)
from ..utils.logging import (
    log_database_operation,
    log_error_with_context,
    log_mcp_tool_call,
)

# FastMCP server instance
mcp = FastMCP("project-kaizen")


@mcp.tool()
async def create_scope(input: CreateScopeInput) -> CreateScopeOutput:
    """Create new scope within namespace with automatic 'default' parent inheritance."""
    log_mcp_tool_call("create_scope", scope=input.scope, description=input.description, parents=input.parents)

    try:
        async with db_manager.acquire() as conn:
            # Parse namespace and scope from input
            namespace_name, scope_name = input.scope.split(":", 1)

            # Get namespace ID
            namespace_query = "SELECT id FROM namespaces WHERE name = $1"
            namespace_result = await conn.fetchrow(namespace_query, namespace_name)

            if not namespace_result:
                raise ValueError(f"Namespace '{namespace_name}' not found")

            namespace_id = namespace_result["id"]

            # Create the scope
            scope_query = """
                INSERT INTO scopes (namespace_id, name, description)
                VALUES ($1, $2, $3)
                RETURNING id
            """

            log_database_operation("INSERT", query="create_scope", params=[namespace_id, scope_name, input.description])
            scope_result = await conn.fetchrow(scope_query, namespace_id, scope_name, input.description)

            if not scope_result:
                raise ValueError(f"Failed to create scope '{input.scope}'")

            scope_id = scope_result["id"]

            # Ensure default parent is included
            all_parents = list(input.parents)
            default_parent = f"{namespace_name}:default"
            if default_parent not in all_parents:
                all_parents.append(default_parent)

            # Add parent relationships
            for parent_scope in all_parents:
                parent_namespace, parent_name = parent_scope.split(":", 1)

                # Get parent scope ID
                parent_query = """
                    SELECT s.id FROM scopes s
                    JOIN namespaces n ON s.namespace_id = n.id
                    WHERE n.name = $1 AND s.name = $2
                """

                parent_result = await conn.fetchrow(parent_query, parent_namespace, parent_name)

                if not parent_result:
                    raise ValueError(f"Parent scope '{parent_scope}' not found")

                parent_id = parent_result["id"]

                # Insert parent relationship
                parent_rel_query = """
                    INSERT INTO scope_parents (child_scope_id, parent_scope_id)
                    VALUES ($1, $2)
                    ON CONFLICT (child_scope_id, parent_scope_id) DO NOTHING
                """

                await conn.execute(parent_rel_query, scope_id, parent_id)

            return CreateScopeOutput(
                scope=input.scope,
                description=input.description,
                parents=all_parents
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "create_scope", "input": input.model_dump()})
        raise


@mcp.tool()
async def update_scope(input: UpdateScopeInput) -> UpdateScopeOutput:
    """Update scope name, description, and parent relationships with automatic reference updating."""
    log_mcp_tool_call("update_scope", scope=input.scope, new_scope=input.new_scope, description=input.description, parents=input.parents)

    try:
        async with db_manager.acquire() as conn:
            # Parse current scope
            current_namespace, current_scope_name = input.scope.split(":", 1)

            # Get current scope ID and namespace ID
            scope_query = """
                SELECT s.id, s.description, n.id as namespace_id, n.name as namespace_name
                FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE n.name = $1 AND s.name = $2
            """

            scope_result = await conn.fetchrow(scope_query, current_namespace, current_scope_name)

            if not scope_result:
                raise ValueError(f"Scope '{input.scope}' not found")

            scope_id = scope_result["id"]
            current_description = scope_result["description"]

            # Handle scope name update if requested
            final_scope_name = input.scope
            if input.new_scope:
                new_namespace, new_scope_name = input.new_scope.split(":", 1)

                # Scope can only be renamed within the same namespace
                if new_namespace != current_namespace:
                    raise ValueError("Cannot move scope to different namespace")

                # Update scope name
                update_scope_query = """
                    UPDATE scopes
                    SET name = $1, updated_at = NOW()
                    WHERE id = $2
                """
                await conn.execute(update_scope_query, new_scope_name, scope_id)
                final_scope_name = input.new_scope

            # Handle description update if requested
            final_description = current_description
            if input.description:
                desc_update_query = """
                    UPDATE scopes
                    SET description = $1, updated_at = NOW()
                    WHERE id = $2
                """
                await conn.execute(desc_update_query, input.description, scope_id)
                final_description = input.description

            # Handle parent relationships update if requested
            final_parents: list[str] = []
            if input.parents is not None:
                # Remove existing parent relationships
                delete_parents_query = "DELETE FROM scope_parents WHERE child_scope_id = $1"
                await conn.execute(delete_parents_query, scope_id)

                # Ensure default parent is preserved
                new_parents = list(input.parents)
                default_parent = f"{current_namespace}:default"
                if default_parent not in new_parents:
                    new_parents.append(default_parent)

                # Add new parent relationships
                for parent_scope in new_parents:
                    parent_namespace, parent_name = parent_scope.split(":", 1)

                    # Get parent scope ID
                    parent_query = """
                        SELECT s.id FROM scopes s
                        JOIN namespaces n ON s.namespace_id = n.id
                        WHERE n.name = $1 AND s.name = $2
                    """

                    parent_result = await conn.fetchrow(parent_query, parent_namespace, parent_name)

                    if not parent_result:
                        raise ValueError(f"Parent scope '{parent_scope}' not found")

                    parent_id = parent_result["id"]

                    # Insert parent relationship
                    parent_rel_query = """
                        INSERT INTO scope_parents (child_scope_id, parent_scope_id)
                        VALUES ($1, $2)
                    """

                    await conn.execute(parent_rel_query, scope_id, parent_id)

                final_parents = new_parents
            else:
                # Get current parents
                parents_query = """
                    SELECT n.name || ':' || s.name as parent_scope
                    FROM scope_parents sp
                    JOIN scopes s ON sp.parent_scope_id = s.id
                    JOIN namespaces n ON s.namespace_id = n.id
                    WHERE sp.child_scope_id = $1
                    ORDER BY parent_scope
                """

                parent_rows = await conn.fetch(parents_query, scope_id)
                final_parents = [row["parent_scope"] for row in parent_rows]

            log_database_operation("UPDATE", query="update_scope_complete", params=[scope_id])

            return UpdateScopeOutput(
                scope=final_scope_name,
                description=final_description,
                parents=final_parents
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "update_scope", "input": input.model_dump()})
        raise


@mcp.tool()
async def delete_scope(input: DeleteScopeInput) -> DeleteScopeOutput:
    """Remove scope and all associated knowledge entries."""
    log_mcp_tool_call("delete_scope", scope=input.scope)

    try:
        async with db_manager.acquire() as conn:
            # Parse scope
            namespace_name, scope_name = input.scope.split(":", 1)

            # Get scope ID and knowledge count
            scope_query = """
                SELECT s.id,
                       (SELECT COUNT(*) FROM knowledge k WHERE k.scope_id = s.id) as knowledge_count
                FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE n.name = $1 AND s.name = $2
            """

            log_database_operation("SELECT", query="delete_scope_info", params=[namespace_name, scope_name])
            scope_result = await conn.fetchrow(scope_query, namespace_name, scope_name)

            if not scope_result:
                raise ValueError(f"Scope '{input.scope}' not found")

            scope_id = scope_result["id"]
            knowledge_count = scope_result["knowledge_count"]

            # Delete scope (cascades to scope_parents and knowledge via foreign keys)
            delete_query = """
                DELETE FROM scopes WHERE id = $1
                RETURNING name
            """

            log_database_operation("DELETE", query="delete_scope", params=[scope_id])
            deleted_result = await conn.fetchrow(delete_query, scope_id)

            if not deleted_result:
                raise ValueError(f"Failed to delete scope '{input.scope}'")

            return DeleteScopeOutput(
                scope=input.scope,
                knowledge_deleted=knowledge_count
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "delete_scope", "input": input.model_dump()})
        raise
