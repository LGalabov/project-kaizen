"""Knowledge repository for database operations."""

from typing import Any
import asyncpg

from ..utils.logging import log_database_operation
from .base import BaseRepository


class KnowledgeRepository(BaseRepository):
    """Repository for knowledge database operations."""
    
    async def create(self, scope_id: int, content: str, context: str) -> str:
        """Create knowledge entry and return ID."""
        result = await self._fetch_one("""
            INSERT INTO knowledge (scope_id, content, context)
            VALUES ($1, $2, $3)
            RETURNING id
        """, scope_id, content, context)

        if not result:
            raise ValueError("Failed to create knowledge entry")

        log_database_operation("INSERT", query="write_knowledge", params=[scope_id, len(content), len(context)])
        return str(result["id"])
        
    async def get_by_id(self, entry_id: str) -> dict[str, Any] | None:
        """Get knowledge entry with scope information."""
        result = await self._fetch_one("""
            SELECT k.scope_id, k.content, k.context, n.name || ':' || s.name as scope_name
            FROM knowledge k
            JOIN scopes s ON k.scope_id = s.id
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE k.id = $1
        """, entry_id)
        
        if not result:
            return None
            
        return {
            "scope_id": result["scope_id"],
            "content": result["content"],
            "context": result["context"],
            "scope_name": result["scope_name"]
        }
    
    async def update(
        self, 
        entry_id: str, 
        content: str | None = None,
        context: str | None = None, 
        scope_id: int | None = None
    ) -> None:
        """Update knowledge entry fields."""
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

        if scope_id:
            param_count += 1
            set_clauses.append(f"scope_id = ${param_count}")
            params.append(scope_id)

        # Always update timestamp
        set_clauses.append("updated_at = NOW()")

        # Add WHERE clause parameter
        param_count += 1
        params.append(entry_id)

        query = f"""
            UPDATE knowledge
            SET {", ".join(set_clauses)}
            WHERE id = ${param_count}
            RETURNING id
        """

        result = await self._fetch_one(query, *params)

        if not result:
            raise ValueError(f"Failed to update knowledge entry '{entry_id}'")

        log_database_operation("UPDATE", query="update_knowledge", params=[entry_id])
    
    async def delete(self, entry_id: str) -> None:
        """Delete knowledge entry."""
        result = await self._fetch_one("""
            DELETE FROM knowledge WHERE id = $1
            RETURNING id
        """, entry_id)

        if not result:
            raise ValueError(f"Knowledge entry '{entry_id}' not found")

        log_database_operation("DELETE", query="delete_knowledge", params=[entry_id])
    
    async def mark_suppressed(self, entry_id: str, active_id: str) -> None:
        """Mark knowledge entry as suppressed by another entry."""
        await self._execute_query("""
            UPDATE knowledge
            SET context = context || ' [SUPPRESSED-BY-' || $1 || ']',
                updated_at = NOW()
            WHERE id = $2
        """, active_id, entry_id)
    
    async def search_by_queries(
        self, 
        queries: list[str], 
        scope_ids: list[int], 
        task_size: str | None = None
    ) -> list[asyncpg.Record]:
        """Search knowledge entries using full-text search."""
        # Create search terms from queries
        search_terms = " | ".join(queries)  # PostgreSQL full-text search OR syntax

        # Build knowledge search query
        query = """
            SELECT k.id, k.content, n.name || ':' || s.name as scope_name,
                   ts_rank_cd(to_tsvector('english', k.content || ' ' || k.context), plainto_tsquery('english', $1)) as rank
            FROM knowledge k
            JOIN scopes s ON k.scope_id = s.id
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE k.scope_id = ANY($2)
              AND (to_tsvector('english', k.content || ' ' || k.context) @@ plainto_tsquery('english', $1))
              AND NOT k.context LIKE '%[SUPPRESSED-%'
        """

        params: list[Any] = [search_terms, scope_ids]

        # Add task size filter if specified
        if task_size:
            query += " AND k.context LIKE $3"
            params.append(f"%{task_size}%")

        query += " ORDER BY rank DESC, k.updated_at DESC LIMIT 50"

        log_database_operation("SELECT", query="get_task_context_search", params=[search_terms, len(scope_ids)])
        return await self._fetch_all(query, *params)
