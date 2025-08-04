"""Scope repository for database operations."""

from typing import Any

from ..utils.logging import log_database_operation
from .base import BaseRepository


class ScopeRepository(BaseRepository):
    """Repository for scope database operations."""
    
    async def create(
        self, 
        namespace_id: int, 
        scope_name: str, 
        description: str, 
        parent_ids: list[int]
    ) -> dict[str, Any]:
        """Create new scope with parent relationships."""
        scope_result = await self._fetch_one("""
            INSERT INTO scopes (namespace_id, name, description)
            VALUES ($1, $2, $3)
            RETURNING id
        """, namespace_id, scope_name, description)

        if not scope_result:
            raise ValueError(f"Failed to create scope '{scope_name}'")

        scope_id = scope_result["id"]

        # Batch insert parent relationships
        if parent_ids:
            await self._execute_query("""
                INSERT INTO scope_parents (child_scope_id, parent_scope_id)
                SELECT * FROM UNNEST($1::BIGINT[], $2::BIGINT[])
                ON CONFLICT (child_scope_id, parent_scope_id) DO NOTHING
            """, [scope_id] * len(parent_ids), parent_ids)

        log_database_operation("INSERT", query="create_scope", params=[namespace_id, scope_name, description])
        return {"id": scope_id}
    
    async def get_by_name(self, namespace_name: str, scope_name: str) -> dict[str, Any] | None:
        """Get scope by namespace and name."""
        result = await self._fetch_one("""
            SELECT s.id, s.description, n.id as namespace_id, n.name as namespace_name
            FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE n.name = $1 AND s.name = $2
        """, namespace_name, scope_name)
        
        if not result:
            return None
            
        return {
            "id": result["id"],
            "description": result["description"],
            "namespace_id": result["namespace_id"],
            "namespace_name": result["namespace_name"]
        }
    
    async def get_parents(self, scope_id: int) -> list[str]:
        """Get parent scope identifiers for a scope."""
        parent_rows = await self._fetch_all("""
            SELECT n.name || ':' || s.name as parent_scope
            FROM scope_parents sp
            JOIN scopes s ON sp.parent_scope_id = s.id
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE sp.child_scope_id = $1
            ORDER BY parent_scope
        """, scope_id)
        
        return [row["parent_scope"] for row in parent_rows]
    
    async def update_name(self, scope_id: int, new_name: str) -> None:
        """Update scope name."""
        await self._execute_query("""
            UPDATE scopes
            SET name = $1, updated_at = NOW()
            WHERE id = $2
        """, new_name, scope_id)
    
    async def update_description(self, scope_id: int, description: str) -> None:
        """Update scope description."""
        await self._execute_query("""
            UPDATE scopes
            SET description = $1, updated_at = NOW()
            WHERE id = $2
        """, description, scope_id)
    
    
    async def update_parents(self, scope_name: str, parent_scope_names: list[str]) -> list[str]:
        """Update scope parent relationships using database function."""
        result = await self._fetch_one("""
            SELECT update_scope_parents($1, $2) as parent_names
        """, scope_name, parent_scope_names)
        
        if not result or result["parent_names"] is None:
            return []
        
        return list(result["parent_names"])
    
    async def delete(self, scope_id: int) -> int:
        """Delete scope and return knowledge count."""
        count_result = await self._fetch_one("""
            SELECT COUNT(*) as knowledge_count
            FROM knowledge k WHERE k.scope_id = $1
        """, scope_id)
        
        knowledge_count = count_result["knowledge_count"] if count_result else 0
        
        deleted_result = await self._fetch_one("""
            DELETE FROM scopes WHERE id = $1
            RETURNING name
        """, scope_id)

        if not deleted_result:
            raise ValueError(f"Failed to delete scope with id {scope_id}")

        log_database_operation("DELETE", query="delete_scope", params=[scope_id])
        return knowledge_count
