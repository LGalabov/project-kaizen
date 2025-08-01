"""Namespace management business logic."""

from typing import Any

from ..models.namespace import NamespaceInfo, NamespaceStyle, ScopeInfo
from ..utils.logging import log_database_operation
from .database_ops import get_db_manager


async def list_namespaces(
    namespace: str | None = None, style: NamespaceStyle = NamespaceStyle.DETAILS
) -> dict[str, NamespaceInfo]:
    """Discover existing namespaces and scopes to decide whether to create new or reuse existing organizational structures."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Base query for namespaces
        namespace_query = "SELECT name, description FROM namespaces"
        params: list[Any] = []

        # Add namespace filter if specified
        if namespace:
            namespace_query += " WHERE name = $1"
            params.append(namespace)

        namespace_query += " ORDER BY name"

        log_database_operation("SELECT", query="get_namespaces", params=params)
        namespace_rows = await conn.fetch(namespace_query, *params)

        namespaces: dict[str, NamespaceInfo] = {}

        for ns_row in namespace_rows:
            namespace_name = ns_row["name"]
            namespaces[namespace_name] = NamespaceInfo(
                description=ns_row["description"]
            )

            # Add scopes based on style
            if style != NamespaceStyle.SHORT:
                scope_query = """
                    SELECT s.name, s.description
                    FROM scopes s
                    JOIN namespaces n ON s.namespace_id = n.id
                    WHERE n.name = $1
                    ORDER BY s.name
                """

                scope_rows = await conn.fetch(scope_query, namespace_name)

                scopes: dict[str, ScopeInfo] = {}
                for scope_row in scope_rows:
                    scopes[scope_row["name"]] = ScopeInfo(
                        description=scope_row["description"]
                    )

                namespaces[namespace_name].scopes = scopes

        return namespaces


async def create_namespace(name: str, description: str) -> dict[str, Any]:
    """Create namespace with automatic 'default' scope."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        namespace_query = """
            INSERT INTO namespaces (name, description)
            VALUES ($1, $2)
            RETURNING id
        """

        log_database_operation(
            "INSERT", query="create_namespace", params=[name, description]
        )
        namespace_result = await conn.fetchrow(namespace_query, name, description)

        if not namespace_result:
            raise ValueError(f"Failed to create namespace '{name}'")

        namespace_id = namespace_result["id"]

        # Create default scope
        scope_query = """
            INSERT INTO scopes (namespace_id, name, description)
            VALUES ($1, $2, $3)
        """

        default_description = f"{description} organization-wide knowledge"
        await conn.execute(scope_query, namespace_id, "default", default_description)

        # Return result with default scope
        scopes: dict[str, ScopeInfo] = {
            "default": ScopeInfo(description=default_description)
        }

        return {"name": name, "description": description, "scopes": scopes}


async def update_namespace(
    name: str, new_name: str | None = None, description: str | None = None
) -> dict[str, Any]:
    """Update namespace name and/or description with automatic reference updating."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Build update query dynamically
        set_clauses: list[str] = []
        params: list[Any] = []
        param_count = 0

        if new_name:
            param_count += 1
            set_clauses.append(f"name = ${param_count}")
            params.append(new_name)

        if description:
            param_count += 1
            set_clauses.append(f"description = ${param_count}")
            params.append(description)

        # Always update the updated_at timestamp
        param_count += 1
        set_clauses.append("updated_at = NOW()")

        # Add WHERE clause parameter
        param_count += 1
        params.append(name)

        update_query = f"""
            UPDATE namespaces
            SET {", ".join(set_clauses)}
            WHERE name = ${param_count}
            RETURNING name, description
        """

        log_database_operation("UPDATE", query="update_namespace", params=params)
        updated_result = await conn.fetchrow(update_query, *params)

        if not updated_result:
            raise ValueError(f"Namespace '{name}' not found")

        # Get all scopes for the updated namespace
        scope_query = """
            SELECT s.name, s.description
            FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE n.name = $1
            ORDER BY s.name
        """

        scope_rows = await conn.fetch(scope_query, updated_result["name"])

        scopes: dict[str, ScopeInfo] = {}
        for scope_row in scope_rows:
            scopes[scope_row["name"]] = ScopeInfo(description=scope_row["description"])

        return {
            "name": updated_result["name"],
            "description": updated_result["description"],
            "scopes": scopes,
        }


async def delete_namespace(name: str) -> dict[str, Any]:
    """Remove namespace and all associated scopes and knowledge entries."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Get counts before deletion for statistics
        count_query = """
            SELECT
                (SELECT COUNT(*) FROM scopes s
                 JOIN namespaces n ON s.namespace_id = n.id
                 WHERE n.name = $1) as scope_count,
                (SELECT COUNT(*) FROM knowledge k
                 JOIN scopes s ON k.scope_id = s.id
                 JOIN namespaces n ON s.namespace_id = n.id
                 WHERE n.name = $1) as knowledge_count
        """

        log_database_operation("SELECT", query="delete_namespace_counts", params=[name])
        counts_result = await conn.fetchrow(count_query, name)

        if counts_result is None:
            raise ValueError(f"Namespace '{name}' not found")

        scope_count = counts_result["scope_count"]
        knowledge_count = counts_result["knowledge_count"]

        # Delete namespace (cascades to scopes and knowledge)
        delete_query = """
            DELETE FROM namespaces WHERE name = $1
            RETURNING name
        """

        log_database_operation("DELETE", query="delete_namespace", params=[name])
        deleted_result = await conn.fetchrow(delete_query, name)

        if not deleted_result:
            raise ValueError(f"Namespace '{name}' not found")

        return {
            "name": name,
            "scopes_count": scope_count,
            "knowledge_count": knowledge_count,
        }
