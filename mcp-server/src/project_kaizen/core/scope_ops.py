"""Scope management business logic."""

from typing import Any

from ..utils.logging import log_database_operation


async def create_scope(
    namespace: str, scope_name: str, description: str, parents: list[str]
) -> dict[str, Any]:
    """Create new scope within namespace with automatic 'default' parent inheritance."""
    from ..server import get_db_pool
    
    pool = get_db_pool()
    async with pool.acquire() as conn:
        # Get namespace ID
        namespace_query = "SELECT id FROM namespaces WHERE name = $1"
        namespace_result = await conn.fetchrow(namespace_query, namespace)

        if not namespace_result:
            raise ValueError(f"Namespace '{namespace}' not found")

        namespace_id = namespace_result["id"]

        # Create the scope
        scope_query = """
            INSERT INTO scopes (namespace_id, name, description)
            VALUES ($1, $2, $3)
            RETURNING id
        """

        log_database_operation(
            "INSERT",
            query="create_scope",
            params=[namespace_id, scope_name, description],
        )
        scope_result = await conn.fetchrow(
            scope_query, namespace_id, scope_name, description
        )

        if not scope_result:
            raise ValueError(f"Failed to create scope '{namespace}:{scope_name}'")

        scope_id = scope_result["id"]

        # Auto-add default parent if not specified
        all_parents = list(parents)
        default_parent = f"{namespace}:default"
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

            parent_result = await conn.fetchrow(
                parent_query, parent_namespace, parent_name
            )

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

        return {
            "scope": f"{namespace}:{scope_name}",
            "description": description,
            "parents": all_parents,
        }


async def update_scope(
    scope: str,
    new_scope: str | None = None,
    description: str | None = None,
    parents: list[str] | None = None,
) -> dict[str, Any]:
    """Update scope name, description, and parent relationships with automatic reference updating."""
    from ..server import get_db_pool
    
    pool = get_db_pool()
    async with pool.acquire() as conn:
        # Parse current scope
        current_namespace, current_scope_name = scope.split(":", 1)

        # Get current scope ID and namespace ID
        scope_query = """
            SELECT s.id, s.description, n.id as namespace_id, n.name as namespace_name
            FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE n.name = $1 AND s.name = $2
        """

        scope_result = await conn.fetchrow(
            scope_query, current_namespace, current_scope_name
        )

        if not scope_result:
            raise ValueError(f"Scope '{scope}' not found")

        scope_id = scope_result["id"]
        current_description = scope_result["description"]

        # Handle scope name update if requested
        final_scope_name = scope
        if new_scope:
            new_namespace, new_scope_name = new_scope.split(":", 1)

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
            final_scope_name = new_scope

        # Handle description update if requested
        final_description = current_description
        if description:
            desc_update_query = """
                UPDATE scopes
                SET description = $1, updated_at = NOW()
                WHERE id = $2
            """
            await conn.execute(desc_update_query, description, scope_id)
            final_description = description

        # Handle parent relationships update if requested
        final_parents: list[str] = []
        if parents is not None:
            # Remove existing parent relationships
            delete_parents_query = "DELETE FROM scope_parents WHERE child_scope_id = $1"
            await conn.execute(delete_parents_query, scope_id)

            # Ensure default parent is preserved
            new_parents = list(parents)
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

                parent_result = await conn.fetchrow(
                    parent_query, parent_namespace, parent_name
                )

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

        log_database_operation(
            "UPDATE", query="update_scope_complete", params=[scope_id]
        )

        return {
            "scope": final_scope_name,
            "description": final_description,
            "parents": final_parents,
        }


async def delete_scope(scope: str) -> dict[str, Any]:
    """Remove scope and all associated knowledge entries."""
    from ..server import get_db_pool
    
    pool = get_db_pool()
    async with pool.acquire() as conn:
        # Parse scope
        namespace_name, scope_name = scope.split(":", 1)

        # Get scope ID and knowledge count
        scope_query = """
            SELECT s.id,
                   (SELECT COUNT(*) FROM knowledge k WHERE k.scope_id = s.id) as knowledge_count
            FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE n.name = $1 AND s.name = $2
        """

        log_database_operation(
            "SELECT", query="delete_scope_info", params=[namespace_name, scope_name]
        )
        scope_result = await conn.fetchrow(scope_query, namespace_name, scope_name)

        if not scope_result:
            raise ValueError(f"Scope '{scope}' not found")

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
            raise ValueError(f"Failed to delete scope '{scope}'")

        return {"scope": scope, "knowledge_deleted": knowledge_count}
