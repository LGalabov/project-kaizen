"""Database operations for Project Kaizen MCP Server."""

from typing import Any, Literal

import asyncpg

from project_kaizen.config import config
from project_kaizen.utils import parse_scope

# Global connection pool (lazy initialization)
_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the database connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            config.database_url,
            min_size=config.database_pool_min,
            max_size=config.database_pool_max,
            command_timeout=60,
        )
    return _pool


async def close_pool() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# ============================================================================
# NAMESPACE OPERATIONS
# ============================================================================


async def get_namespaces(
    namespace: str | None, style: Literal["short", "long", "details"]
) -> dict[str, Any]:
    """Query namespaces and format response based on style."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Get namespaces
        if namespace:
            query = "SELECT * FROM namespaces WHERE name = $1"
            rows = await conn.fetch(query, namespace)
        else:
            query = "SELECT * FROM namespaces ORDER BY name"
            rows = await conn.fetch(query)

        result: dict[str, Any] = {"namespaces": {}}

        for row in rows:
            ns_name = row["name"]
            result["namespaces"][ns_name] = {"description": row["description"]}

            # Add scopes for long and details styles
            if style in ["long", "details"]:
                scopes_query = """
                    SELECT s.name, s.description
                    FROM scopes s
                    JOIN namespaces n ON s.namespace_id = n.id
                    WHERE n.name = $1
                    ORDER BY s.name
                """
                scope_rows = await conn.fetch(scopes_query, ns_name)

                result["namespaces"][ns_name]["scopes"] = {}
                for scope_row in scope_rows:
                    scope_data = {"description": scope_row["description"]}

                    # Add parent relationships for details style
                    if style == "details":
                        parents_query = """
                            SELECT ps.name as parent_name, pn.name as parent_namespace
                            FROM scope_parents sp
                            JOIN scopes s ON sp.child_scope_id = s.id
                            JOIN scopes ps ON sp.parent_scope_id = ps.id
                            JOIN namespaces pn ON ps.namespace_id = pn.id
                            WHERE s.name = $1 AND s.namespace_id = (
                                SELECT id FROM namespaces WHERE name = $2
                            )
                            ORDER BY pn.name, ps.name
                        """
                        parent_rows = await conn.fetch(parents_query, scope_row["name"], ns_name)
                        scope_data["parents"] = [
                            f"{p['parent_namespace']}:{p['parent_name']}" for p in parent_rows
                        ]

                    result["namespaces"][ns_name]["scopes"][scope_row["name"]] = scope_data

        return result


async def create_namespace(namespace: str, description: str) -> dict[str, Any]:
    """Create namespace with automatic default scope (handled by trigger)."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Create namespace - trigger will create default scope
            ns_id = await conn.fetchval(
                "INSERT INTO namespaces (name, description) VALUES ($1, $2) RETURNING id",
                namespace,
                description,
            )

            # Get the auto-created default scope
            default_scope = await conn.fetchrow(
                "SELECT description FROM scopes WHERE namespace_id = $1 AND name = 'default'", ns_id
            )

            return {
                "name": namespace,
                "description": description,
                "scopes": {
                    "default": {
                        "description": default_scope["description"]
                        if default_scope
                        else f"{namespace} - default scope"
                    }
                },
            }


async def update_namespace(
    namespace: str, new_namespace: str | None, new_description: str | None
) -> dict[str, Any]:
    """Update namespace with cascade updates."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Build update query
        updates = []
        params: list[Any] = []
        param_count = 1

        if new_namespace:
            updates.append(f"name = ${param_count}")
            params.append(new_namespace)
            param_count += 1

        if new_description:
            updates.append(f"description = ${param_count}")
            params.append(new_description)
            param_count += 1

        # Validation ensures at least one update is provided
        params.append(namespace)
        query = f"""
            UPDATE namespaces
            SET {", ".join(updates)}, updated_at = NOW()
            WHERE name = ${param_count}
            RETURNING name, description
        """
        row = await conn.fetchrow(query, *params)
        if not row:
            raise ValueError(f"Namespace '{namespace}' not found")

        return {
            "name": row["name"],
            "description": row["description"],
            "scopes": {"default": {"description": f"{row['name']} - default scope"}},
        }


async def delete_namespace(namespace: str) -> dict[str, Any]:
    """Delete namespace and return statistics."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Get statistics before deletion
            stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(DISTINCT s.id) as scope_count,
                    COUNT(DISTINCT k.id) as knowledge_count
                FROM namespaces n
                LEFT JOIN scopes s ON n.id = s.namespace_id
                LEFT JOIN knowledge k ON s.id = k.scope_id
                WHERE n.name = $1
            """,
                namespace,
            )

            if stats is None:
                raise ValueError(f"Namespace '{namespace}' not found")

            # Delete namespace (cascades to scopes and knowledge)
            await conn.execute("DELETE FROM namespaces WHERE name = $1", namespace)

            return {
                "name": namespace,
                "scopes_count": stats["scope_count"] or 0,
                "knowledge_count": stats["knowledge_count"] or 0,
            }


# ============================================================================
# SCOPE OPERATIONS
# ============================================================================


async def create_scope(scope: str, description: str, parents: list[str] | None) -> dict[str, Any]:
    """Create scope with parent relationships."""
    namespace, scope_name = parse_scope(scope)
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Get namespace ID
            ns_id = await conn.fetchval("SELECT id FROM namespaces WHERE name = $1", namespace)
            if not ns_id:
                raise ValueError(f"Namespace '{namespace}' not found")

            # Create scope - trigger will add default parent
            scope_id = await conn.fetchval(
                """INSERT INTO scopes (namespace_id, name, description)
                VALUES ($1, $2, $3) RETURNING id""",
                ns_id,
                scope_name,
                description,
            )

            # Add explicit parent relationships
            if parents:
                for parent in parents:
                    parent_ns, parent_name = parse_scope(parent)

                    # Get parent scope ID
                    parent_id = await conn.fetchval(
                        """
                        SELECT s.id FROM scopes s
                        JOIN namespaces n ON s.namespace_id = n.id
                        WHERE n.name = $1 AND s.name = $2
                        """,
                        parent_ns,
                        parent_name,
                    )

                    if parent_id and parent_id != scope_id:
                        # Add parent relationship (skip if would be self-reference)
                        await conn.execute(
                            """
                            INSERT INTO scope_parents (child_scope_id, parent_scope_id)
                            VALUES ($1, $2)
                            ON CONFLICT DO NOTHING
                            """,
                            scope_id,
                            parent_id,
                        )

            # Get final parent relationships
            parent_rows = await conn.fetch(
                """
                SELECT n.name as ns_name, s.name as scope_name
                FROM scope_parents sp
                JOIN scopes s ON sp.parent_scope_id = s.id
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE sp.child_scope_id = $1
                ORDER BY n.name, s.name
                """,
                scope_id,
            )

            return {
                "scope": scope,
                "description": description,
                "parents": [f"{p['ns_name']}:{p['scope_name']}" for p in parent_rows],
            }


async def update_scope(
    scope: str,
    new_scope: str | None,
    new_description: str | None,
    new_parents: list[str] | None,
) -> dict[str, Any]:
    """Update scope and relationships."""
    namespace, scope_name = parse_scope(scope)
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Get namespace and scope IDs
            ids = await conn.fetchrow(
                """
                SELECT n.id as ns_id, s.id as scope_id
                FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE n.name = $1 AND s.name = $2
                """,
                namespace,
                scope_name,
            )

            if not ids:
                raise ValueError(f"Scope '{scope}' not found")

            scope_id = ids["scope_id"]

            # Update scope name/description if provided
            if new_scope or new_description:
                updates = []
                params = []
                param_count = 1

                if new_scope:
                    new_namespace, new_scope_name = parse_scope(new_scope)
                    if new_namespace != namespace:
                        raise ValueError("Cannot change namespace of scope")
                    updates.append(f"name = ${param_count}")
                    params.append(new_scope_name)
                    param_count += 1

                if new_description:
                    updates.append(f"description = ${param_count}")
                    params.append(new_description)
                    param_count += 1

                params.append(scope_id)
                await conn.execute(
                    f"""
                    UPDATE scopes
                    SET {", ".join(updates)}, updated_at = NOW()
                    WHERE id = ${param_count}
                    """,
                    *params,
                )

            # Update parent relationships if provided
            if new_parents is not None:
                # Use database function to update parents (handles default parent)
                parent_array = new_parents if new_parents else []
                await conn.fetchval("SELECT update_scope_parents($1, $2)", scope, parent_array)

            # Get final state
            final_scope = new_scope or scope
            row = await conn.fetchrow("SELECT description FROM scopes WHERE id = $1", scope_id)

            # Get parent relationships
            parent_rows = await conn.fetch(
                """
                SELECT n.name as ns_name, s.name as scope_name
                FROM scope_parents sp
                JOIN scopes s ON sp.parent_scope_id = s.id
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE sp.child_scope_id = $1
                ORDER BY n.name, s.name
                """,
                scope_id,
            )

            return {
                "scope": final_scope,
                "description": row["description"],
                "parents": [f"{p['ns_name']}:{p['scope_name']}" for p in parent_rows],
            }


async def delete_scope(scope: str) -> dict[str, Any]:
    """Delete scope and return statistics."""
    namespace, scope_name = parse_scope(scope)
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Get statistics
            result = await conn.fetchrow(
                """
                SELECT s.id, COUNT(k.id) as knowledge_count
                FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                LEFT JOIN knowledge k ON s.id = k.scope_id
                WHERE n.name = $1 AND s.name = $2
                GROUP BY s.id
                """,
                namespace,
                scope_name,
            )

            if not result:
                raise ValueError(f"Scope '{scope}' not found")

            # Delete scope (will be prevented by trigger if it's a default scope)
            try:
                await conn.execute("DELETE FROM scopes WHERE id = $1", result["id"])
            except asyncpg.exceptions.RaiseException as e:
                if "Cannot delete the default scope" in str(e):
                    raise ValueError("Cannot delete default scope") from e
                raise

            return {"scope": scope, "knowledge_deleted": result["knowledge_count"] or 0}


# ============================================================================
# KNOWLEDGE OPERATIONS
# ============================================================================


async def write_knowledge(
    scope: str, content: str, context: str, task_size: Literal["XS", "S", "M", "L", "XL"] | None
) -> dict[str, Any]:
    """Create new knowledge entry."""
    namespace, scope_name = parse_scope(scope)
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Get scope ID
        scope_id = await conn.fetchval(
            """
            SELECT s.id FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE n.name = $1 AND s.name = $2
            """,
            namespace,
            scope_name,
        )

        if not scope_id:
            raise ValueError(f"Scope '{scope}' not found")

        # Insert knowledge entry (search vectors are auto-generated)
        knowledge_id = await conn.fetchval(
            """
            INSERT INTO knowledge (scope_id, content, context, task_size)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            scope_id,
            content,
            context,
            task_size,
        )

        return {"id": knowledge_id, "scope": scope}


async def update_knowledge(
    knowledge_id: int,
    content: str | None,
    context: str | None,
    scope: str | None,
    task_size: Literal["XS", "S", "M", "L", "XL"] | None,
) -> dict[str, Any]:
    """Update knowledge entry."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Build update query
        updates = []
        params: list[Any] = []
        param_count = 1

        if content is not None:
            updates.append(f"content = ${param_count}")
            params.append(content)
            param_count += 1

        if context is not None:
            updates.append(f"context = ${param_count}")
            params.append(context)
            param_count += 1

        if task_size is not None:
            updates.append(f"task_size = ${param_count}")
            params.append(task_size)
            param_count += 1

        if scope is not None:
            namespace, scope_name = parse_scope(scope)
            scope_id = await conn.fetchval(
                """
                SELECT s.id FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE n.name = $1 AND s.name = $2
                """,
                namespace,
                scope_name,
            )

            if not scope_id:
                raise ValueError(f"Scope '{scope}' not found")

            updates.append(f"scope_id = ${param_count}")
            params.append(scope_id)
            param_count += 1

        # Validation ensures at least one update is provided
        params.append(knowledge_id)
        query = f"""
            UPDATE knowledge
            SET {", ".join(updates)}, updated_at = NOW()
            WHERE id = ${param_count}
            RETURNING id
        """

        result = await conn.fetchval(query, *params)
        if not result:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        return {"id": knowledge_id, "scope": scope or "unchanged"}


async def delete_knowledge(knowledge_id: int) -> dict[str, Any]:
    """Delete knowledge entry."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        deleted = await conn.execute("DELETE FROM knowledge WHERE id = $1", knowledge_id)

        if "DELETE 0" in deleted:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        return {"id": knowledge_id}


async def resolve_conflict(active_id: int, suppressed_ids: list[int]) -> dict[str, Any]:
    """Mark knowledge entries as suppressed using knowledge_conflicts table."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # IDs are already integers, no conversion needed

            # Check if active entry exists
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM knowledge WHERE id = $1)", active_id
            )
            if not exists:
                raise ValueError(f"Active knowledge entry {active_id} not found")

            # Create conflict record
            await conn.execute(
                """
                INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids)
                VALUES ($1, $2)
                """,
                active_id,
                suppressed_ids,
            )

            return {"active_id": active_id, "suppressed_ids": suppressed_ids}


async def get_task_context(
    queries: list[str], scope: str, task_size: Literal["XS", "S", "M", "L", "XL"] | None
) -> dict[str, dict[int, str]]:
    """Search knowledge using database function with scope hierarchy."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Use the database function for scope-specific search
        rows = await conn.fetch(
            "SELECT * FROM get_task_context($1, $2, $3)", queries, scope, task_size
        )

        # Organize results by scope
        result: dict[str, dict[int, str]] = {}
        for row in rows:
            scope_key = row["qualified_scope_name"]
            if scope_key not in result:
                result[scope_key] = {}
            result[scope_key][row["knowledge_id"]] = row["content"]

        return result
