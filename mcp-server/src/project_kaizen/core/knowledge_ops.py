"""Knowledge management business logic."""

import secrets
import string
from typing import Any

from .database_ops import get_db_manager
from ..utils.logging import log_database_operation


def generate_knowledge_id() -> str:
    """Generate a unique knowledge entry ID."""
    # Generate 10-character alphanumeric ID
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(10))


async def create_knowledge_entry(scope: str, content: str, context: str) -> str:
    """Create knowledge entry - pure business logic."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Parse scope
        namespace_name, scope_name = scope.split(":", 1)

        # Get scope ID
        scope_query = """
            SELECT s.id FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE n.name = $1 AND s.name = $2
        """

        scope_result = await conn.fetchrow(scope_query, namespace_name, scope_name)

        if not scope_result:
            raise ValueError(f"Scope '{scope}' not found")

        scope_id = scope_result["id"]

        # Insert knowledge entry (ID auto-generated, task_size can be NULL)
        knowledge_query = """
            INSERT INTO knowledge (scope_id, content, context)
            VALUES ($1, $2, $3)
            RETURNING id
        """

        log_database_operation("INSERT", query="write_knowledge", params=[scope_id, len(content), len(context)])
        result = await conn.fetchrow(knowledge_query, scope_id, content, context)

        if not result:
            raise ValueError("Failed to create knowledge entry")

        return str(result["id"])


async def update_knowledge_entry(entry_id: str, content: str | None = None, context: str | None = None, scope: str | None = None) -> str:
    """Update knowledge entry - pure business logic."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Get current knowledge entry
        current_query = """
            SELECT k.scope_id, k.content, k.context, n.name || ':' || s.name as current_scope
            FROM knowledge k
            JOIN scopes s ON k.scope_id = s.id
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE k.id = $1
        """

        current_result = await conn.fetchrow(current_query, entry_id)

        if not current_result:
            raise ValueError(f"Knowledge entry '{entry_id}' not found")

        current_scope_id = current_result["scope_id"]
        current_scope = current_result["current_scope"]

        # Handle scope change if requested
        final_scope_id = current_scope_id
        final_scope = current_scope

        if scope:
            namespace_name, scope_name = scope.split(":", 1)

            # Get new scope ID
            scope_query = """
                SELECT s.id FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE n.name = $1 AND s.name = $2
            """

            scope_result = await conn.fetchrow(scope_query, namespace_name, scope_name)

            if not scope_result:
                raise ValueError(f"Target scope '{scope}' not found")

            final_scope_id = scope_result["id"]
            final_scope = scope

        # Build update query dynamically
        set_clauses: list[str] = []
        params: list[Any] = []
        param_count = 0

        if content:
            param_count += 1
            set_clauses.append(f"content = ${param_count}")
            params.append(content)

        if context:
            param_count += 1
            set_clauses.append(f"context = ${param_count}")
            params.append(context)

        if scope:
            param_count += 1
            set_clauses.append(f"scope_id = ${param_count}")
            params.append(final_scope_id)

        # Always update timestamp
        set_clauses.append("updated_at = NOW()")

        # Add WHERE clause parameter
        param_count += 1
        params.append(entry_id)

        update_query = f"""
            UPDATE knowledge
            SET {', '.join(set_clauses)}
            WHERE id = ${param_count}
            RETURNING id
        """

        log_database_operation("UPDATE", query="update_knowledge", params=[entry_id])
        update_result = await conn.fetchrow(update_query, *params)

        if not update_result:
            raise ValueError(f"Failed to update knowledge entry '{entry_id}'")

        return final_scope


async def delete_knowledge_entry(entry_id: str) -> str:
    """Remove knowledge entry from system."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Delete knowledge entry
        delete_query = """
            DELETE FROM knowledge WHERE id = $1
            RETURNING id
        """

        log_database_operation("DELETE", query="delete_knowledge", params=[entry_id])
        deleted_result = await conn.fetchrow(delete_query, entry_id)

        if not deleted_result:
            raise ValueError(f"Knowledge entry '{entry_id}' not found")

        return entry_id


async def resolve_knowledge_conflicts(active_id: str, suppressed_ids: list[str]) -> tuple[str, list[str]]:
    """Mark knowledge entries for conflict resolution when contradictory information exists."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Verify active knowledge exists
        active_query = "SELECT id FROM knowledge WHERE id = $1"
        active_result = await conn.fetchrow(active_query, active_id)

        if not active_result:
            raise ValueError(f"Active knowledge entry '{active_id}' not found")

        # Verify all suppressed knowledge entries exist
        for suppressed_id in suppressed_ids:
            suppressed_query = "SELECT id FROM knowledge WHERE id = $1"
            suppressed_result = await conn.fetchrow(suppressed_query, suppressed_id)

            if not suppressed_result:
                raise ValueError(f"Suppressed knowledge entry '{suppressed_id}' not found")

        # Mark suppressed entries
        for suppressed_id in suppressed_ids:
            suppress_query = """
                UPDATE knowledge
                SET context = context || ' [SUPPRESSED-BY-' || $1 || ']',
                    updated_at = NOW()
                WHERE id = $2
            """

            await conn.execute(suppress_query, active_id, suppressed_id)

        log_database_operation("UPDATE", query="suppress_knowledge_conflicts", params=[active_id, len(suppressed_ids)])

        return active_id, suppressed_ids


async def get_task_context_knowledge(queries: list[str], scope: str, task_size: str | None = None) -> dict[str, dict[str, str]]:
    """AI provides multiple targeted queries for complex tasks, returns relevant knowledge organized by scope hierarchy."""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Parse starting scope
        namespace_name, scope_name = scope.split(":", 1)

        # Get scope hierarchy (scope + all ancestors)
        hierarchy_query = """
            WITH RECURSIVE scope_ancestors AS (
                -- Base case: starting scope
                SELECT s.id, s.name, n.name as namespace_name, 0 as level
                FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE n.name = $1 AND s.name = $2

                UNION ALL

                -- Recursive case: parent scopes
                SELECT ps.id, ps.name, pn.name as namespace_name, sa.level + 1
                FROM scope_ancestors sa
                JOIN scope_parents sp ON sa.id = sp.child_scope_id
                JOIN scopes ps ON sp.parent_scope_id = ps.id
                JOIN namespaces pn ON ps.namespace_id = pn.id
            )
            SELECT DISTINCT id, namespace_name || ':' || name as scope_name, level
            FROM scope_ancestors
            ORDER BY level ASC
        """

        hierarchy_result = await conn.fetch(hierarchy_query, namespace_name, scope_name)

        if not hierarchy_result:
            raise ValueError(f"Scope '{scope}' not found")

        # Build search query with full-text search across all hierarchy scopes
        scope_ids = [row["id"] for row in hierarchy_result]

        # Create search terms from queries
        search_terms = " | ".join(queries)  # PostgreSQL full-text search OR syntax

        # Build knowledge search query
        knowledge_query = """
            SELECT k.id, k.content, n.name || ':' || s.name as scope_name,
                   ts_rank_cd(to_tsvector('english', k.content || ' ' || k.context), plainto_tsquery('english', $1)) as rank
            FROM knowledge k
            JOIN scopes s ON k.scope_id = s.id
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE k.scope_id = ANY($2)
              AND (to_tsvector('english', k.content || ' ' || k.context) @@ plainto_tsquery('english', $1))
              AND NOT k.context LIKE '%[SUPPRESSED-%'  -- Exclude suppressed entries
        """

        query_params: list[Any] = [search_terms, scope_ids]

        # Add task size filter if specified
        if task_size:
            knowledge_query += " AND k.context LIKE $3"
            query_params.append(f"%{task_size}%")

        knowledge_query += " ORDER BY rank DESC, k.updated_at DESC LIMIT 50"

        log_database_operation("SELECT", query="get_task_context_search", params=[search_terms, len(scope_ids)])
        knowledge_results = await conn.fetch(knowledge_query, *query_params)

        # Organize results by scope hierarchy
        results: dict[str, dict[str, str]] = {}

        for row in knowledge_results:
            scope_name = row["scope_name"]
            knowledge_id = row["id"]
            content = row["content"]

            if scope_name not in results:
                results[scope_name] = {}

            results[scope_name][knowledge_id] = content

        return results