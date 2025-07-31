"""MCP tools for knowledge management operations."""

import secrets
import string
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..database import db_manager
from ..models.knowledge import (
    DeleteKnowledgeInput,
    DeleteKnowledgeOutput,
    GetTaskContextInput,
    GetTaskContextOutput,
    ResolveKnowledgeConflictInput,
    ResolveKnowledgeConflictOutput,
    UpdateKnowledgeInput,
    UpdateKnowledgeOutput,
    WriteKnowledgeInput,
    WriteKnowledgeOutput,
)
from ..utils.logging import (
    log_database_operation,
    log_error_with_context,
    log_mcp_tool_call,
)

# FastMCP server instance
mcp = FastMCP("project-kaizen")


def generate_knowledge_id() -> str:
    """Generate a unique knowledge entry ID."""
    # Generate 10-character alphanumeric ID
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(10))


@mcp.tool()
async def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
    """Store new knowledge entry with automatic scope assignment and context tagging."""
    log_mcp_tool_call("write_knowledge", scope=input.scope, content_length=len(input.content), context=input.context[:50])

    try:
        async with db_manager.acquire() as conn:
            # Parse scope
            namespace_name, scope_name = input.scope.split(":", 1)

            # Get scope ID
            scope_query = """
                SELECT s.id FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE n.name = $1 AND s.name = $2
            """

            scope_result = await conn.fetchrow(scope_query, namespace_name, scope_name)

            if not scope_result:
                raise ValueError(f"Scope '{input.scope}' not found")

            scope_id = scope_result["id"]

            # Insert knowledge entry (ID auto-generated, task_size can be NULL)
            knowledge_query = """
                INSERT INTO knowledge (scope_id, content, context)
                VALUES ($1, $2, $3)
                RETURNING id
            """

            log_database_operation("INSERT", query="write_knowledge", params=[scope_id, len(input.content), len(input.context)])
            result = await conn.fetchrow(knowledge_query, scope_id, input.content, input.context)

            if not result:
                raise ValueError("Failed to create knowledge entry")

            knowledge_id = str(result["id"])

            return WriteKnowledgeOutput(
                id=knowledge_id,
                scope=input.scope
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "write_knowledge", "input": input.model_dump()})
        raise


@mcp.tool()
async def update_knowledge(input: UpdateKnowledgeInput) -> UpdateKnowledgeOutput:
    """Update knowledge entry content, context, or scope assignment."""
    log_mcp_tool_call("update_knowledge", id=input.id, content_length=len(input.content) if input.content else None, scope=input.scope)

    try:
        async with db_manager.acquire() as conn:
            # Get current knowledge entry
            current_query = """
                SELECT k.scope_id, k.content, k.context, n.name || ':' || s.name as current_scope
                FROM knowledge k
                JOIN scopes s ON k.scope_id = s.id
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE k.id = $1
            """

            current_result = await conn.fetchrow(current_query, input.id)

            if not current_result:
                raise ValueError(f"Knowledge entry '{input.id}' not found")

            current_scope_id = current_result["scope_id"]
            current_scope = current_result["current_scope"]

            # Handle scope change if requested
            final_scope_id = current_scope_id
            final_scope = current_scope

            if input.scope:
                namespace_name, scope_name = input.scope.split(":", 1)

                # Get new scope ID
                scope_query = """
                    SELECT s.id FROM scopes s
                    JOIN namespaces n ON s.namespace_id = n.id
                    WHERE n.name = $1 AND s.name = $2
                """

                scope_result = await conn.fetchrow(scope_query, namespace_name, scope_name)

                if not scope_result:
                    raise ValueError(f"Target scope '{input.scope}' not found")

                final_scope_id = scope_result["id"]
                final_scope = input.scope

            # Build update query dynamically
            set_clauses: list[str] = []
            params: list[Any] = []
            param_count = 0

            if input.content:
                param_count += 1
                set_clauses.append(f"content = ${param_count}")
                params.append(input.content)

            if input.context:
                param_count += 1
                set_clauses.append(f"context = ${param_count}")
                params.append(input.context)

            if input.scope:
                param_count += 1
                set_clauses.append(f"scope_id = ${param_count}")
                params.append(final_scope_id)

            # Always update timestamp
            set_clauses.append("updated_at = NOW()")

            # Add WHERE clause parameter
            param_count += 1
            params.append(input.id)

            update_query = f"""
                UPDATE knowledge
                SET {', '.join(set_clauses)}
                WHERE id = ${param_count}
                RETURNING id
            """

            log_database_operation("UPDATE", query="update_knowledge", params=[input.id])
            update_result = await conn.fetchrow(update_query, *params)

            if not update_result:
                raise ValueError(f"Failed to update knowledge entry '{input.id}'")

            return UpdateKnowledgeOutput(
                id=input.id,
                scope=final_scope
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "update_knowledge", "input": input.model_dump()})
        raise


@mcp.tool()
async def delete_knowledge(input: DeleteKnowledgeInput) -> DeleteKnowledgeOutput:
    """Remove knowledge entry from system."""
    log_mcp_tool_call("delete_knowledge", id=input.id)

    try:
        async with db_manager.acquire() as conn:
            # Delete knowledge entry
            delete_query = """
                DELETE FROM knowledge WHERE id = $1
                RETURNING id
            """

            log_database_operation("DELETE", query="delete_knowledge", params=[input.id])
            deleted_result = await conn.fetchrow(delete_query, input.id)

            if not deleted_result:
                raise ValueError(f"Knowledge entry '{input.id}' not found")

            return DeleteKnowledgeOutput(id=input.id)

    except Exception as e:
        log_error_with_context(e, {"tool": "delete_knowledge", "input": input.model_dump()})
        raise


@mcp.tool()
async def resolve_knowledge_conflict(input: ResolveKnowledgeConflictInput) -> ResolveKnowledgeConflictOutput:
    """Mark knowledge entries for conflict resolution when contradictory information exists."""
    log_mcp_tool_call("resolve_knowledge_conflict", active_id=input.active_id, suppressed_count=len(input.suppressed_ids))

    try:
        async with db_manager.acquire() as conn:
            # Verify active knowledge exists
            active_query = "SELECT id FROM knowledge WHERE id = $1"
            active_result = await conn.fetchrow(active_query, input.active_id)

            if not active_result:
                raise ValueError(f"Active knowledge entry '{input.active_id}' not found")

            # Verify all suppressed knowledge entries exist
            for suppressed_id in input.suppressed_ids:
                suppressed_query = "SELECT id FROM knowledge WHERE id = $1"
                suppressed_result = await conn.fetchrow(suppressed_query, suppressed_id)

                if not suppressed_result:
                    raise ValueError(f"Suppressed knowledge entry '{suppressed_id}' not found")

            # Mark suppressed entries (assuming there's a suppressed column or similar mechanism)
            # Note: This implementation assumes we add a 'suppressed' boolean column to knowledge table
            # For now, we'll use a simple approach of updating a status or adding metadata

            for suppressed_id in input.suppressed_ids:
                suppress_query = """
                    UPDATE knowledge
                    SET context = context || ' [SUPPRESSED-BY-' || $1 || ']',
                        updated_at = NOW()
                    WHERE id = $2
                """

                await conn.execute(suppress_query, input.active_id, suppressed_id)

            log_database_operation("UPDATE", query="suppress_knowledge_conflicts", params=[input.active_id, len(input.suppressed_ids)])

            return ResolveKnowledgeConflictOutput(
                active_id=input.active_id,
                suppressed_ids=input.suppressed_ids
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "resolve_knowledge_conflict", "input": input.model_dump()})
        raise


@mcp.tool()
async def get_task_context(input: GetTaskContextInput) -> GetTaskContextOutput:
    """AI provides multiple targeted queries for complex tasks, MCP returns relevant knowledge organized by scope hierarchy."""
    log_mcp_tool_call("get_task_context", queries=input.queries, scope=input.scope, task_size=input.task_size.value if input.task_size else None)

    try:
        async with db_manager.acquire() as conn:
            # Parse starting scope
            namespace_name, scope_name = input.scope.split(":", 1)

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
                raise ValueError(f"Scope '{input.scope}' not found")

            # Build search query with full-text search across all hierarchy scopes
            scope_ids = [row["id"] for row in hierarchy_result]

            # Create search terms from queries
            search_terms = " | ".join(input.queries)  # PostgreSQL full-text search OR syntax

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
            if input.task_size:
                knowledge_query += " AND k.context LIKE $3"
                query_params.append(f"%{input.task_size.value}%")

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

            return GetTaskContextOutput(results=results)

    except Exception as e:
        log_error_with_context(e, {"tool": "get_task_context", "input": input.model_dump()})
        raise
