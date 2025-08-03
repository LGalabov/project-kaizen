"""Namespace management business logic."""

from typing import Any

from ..models.namespace import NamespaceData, NamespaceStyle, ScopeData
from ..utils.logging import log_database_operation


async def list_namespaces(
    namespace: str | None = None, style: NamespaceStyle = NamespaceStyle.SHORT
) -> dict[str, NamespaceData]:
    """Discover existing namespaces and scopes in spec-compliant nested dictionary format."""
    from ..server import get_db_pool
    
    pool = get_db_pool()
    async with pool.acquire() as conn:
        # Build base query for namespaces
        if namespace:
            ns_query = "SELECT name, description FROM namespaces WHERE name = $1 ORDER BY name"
            params = [namespace]
        else:
            ns_query = "SELECT name, description FROM namespaces ORDER BY name"
            params = []

        log_database_operation("SELECT", query="get_namespaces", params=params)
        namespace_rows = await conn.fetch(ns_query, *params)

        # Build result dictionary
        result: dict[str, NamespaceData] = {}
        
        for ns_row in namespace_rows:
            ns_name = ns_row["name"]
            ns_description = ns_row["description"]
            
            # For SHORT style, only include description (no scopes)
            if style == NamespaceStyle.SHORT:
                result[ns_name] = NamespaceData(description=ns_description, scopes=None)
                continue
            
            # For LONG and DETAILS styles, include scopes
            scope_query = """
                SELECT s.name, s.description, s.id
                FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                WHERE n.name = $1
                ORDER BY s.name
            """
            scope_rows = await conn.fetch(scope_query, ns_name)
            
            scopes_dict: dict[str, ScopeData] = {}
            for scope_row in scope_rows:
                scope_name = scope_row["name"]
                scope_description = scope_row["description"]
                
                if style == NamespaceStyle.DETAILS:
                    # Get parent information for DETAILS style
                    parent_query = """
                        SELECT n.name || ':' || s.name as parent_scope
                        FROM scope_parents sp
                        JOIN scopes s ON sp.parent_scope_id = s.id
                        JOIN namespaces n ON s.namespace_id = n.id
                        WHERE sp.child_scope_id = $1
                        ORDER BY parent_scope
                    """
                    parent_rows = await conn.fetch(parent_query, scope_row["id"])
                    parents = [p["parent_scope"] for p in parent_rows]
                    scopes_dict[scope_name] = ScopeData(description=scope_description, parents=parents)
                else:
                    scopes_dict[scope_name] = ScopeData(description=scope_description, parents=None)
            
            result[ns_name] = NamespaceData(description=ns_description, scopes=scopes_dict)
        
        return result


async def create_namespace(name: str, description: str) -> dict[str, Any]:
    """Create namespace with automatic 'default' scope."""
    from ..server import get_db_pool
    
    pool = get_db_pool()
    async with pool.acquire() as conn:
        # Insert namespace (trigger will create default scope)
        ns_result = await conn.fetchrow("""
            INSERT INTO namespaces (name, description) 
            VALUES ($1, $2) 
            RETURNING id, name, description
        """, name, description)

        if not ns_result:
            raise ValueError(f"Failed to create namespace '{name}'")
        
        # Get the auto-created default scope
        scope_result = await conn.fetchrow("""
            SELECT name, description
            FROM scopes s
            WHERE s.namespace_id = $1 AND s.name = 'default'
        """, ns_result["id"])
        
        if not scope_result:
            raise ValueError(f"Default scope not created for namespace '{name}'")

        scopes_dict = {
            scope_result["name"]: ScopeData(
                description=scope_result["description"],
                parents=None
            )
        }

        return {
            "name": ns_result["name"],
            "description": ns_result["description"],
            "scopes": scopes_dict
        }


async def update_namespace(
    name: str, new_name: str | None = None, description: str | None = None
) -> dict[str, Any]:
    """Update namespace name and/or description."""
    from ..server import get_db_pool
    
    if not new_name and not description:
        raise ValueError("Either new_name or description must be provided")
    
    pool = get_db_pool()
    async with pool.acquire() as conn:
        # Build UPDATE query dynamically
        updates = []
        params = []
        param_idx = 1

        if new_name:
            updates.append(f"name = ${param_idx}")
            params.append(new_name)
            param_idx += 1

        if description:
            updates.append(f"description = ${param_idx}")
            params.append(description)
            param_idx += 1

        updates.append("updated_at = NOW()")
        params.append(name)  # WHERE clause parameter

        query = f"""
            UPDATE namespaces 
            SET {", ".join(updates)}
            WHERE name = ${param_idx}
            RETURNING name, description
        """

        log_database_operation("UPDATE", query="update_namespace", params=params)
        result = await conn.fetchrow(query, *params)

        if not result:
            raise ValueError(f"Namespace '{name}' not found")

        # Get all scopes for the updated namespace
        scope_rows = await conn.fetch("""
            SELECT s.name, s.description
            FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE n.name = $1
            ORDER BY s.name
        """, result["name"])

        scopes_dict = {
            row["name"]: ScopeData(
                description=row["description"],
                parents=None
            )
            for row in scope_rows
        }

        return {
            "name": result["name"],
            "description": result["description"],
            "scopes": scopes_dict
        }


async def delete_namespace(name: str) -> dict[str, Any]:
    """Remove namespace and all associated scopes and knowledge entries."""
    from ..server import get_db_pool
    
    pool = get_db_pool()
    async with pool.acquire() as conn:
        # Get counts and delete in single transaction
        result = await conn.fetchrow("""
            WITH counts AS (
                SELECT 
                    COUNT(DISTINCT s.id) as scope_count,
                    COUNT(k.id) as knowledge_count
                FROM namespaces n
                LEFT JOIN scopes s ON s.namespace_id = n.id
                LEFT JOIN knowledge k ON k.scope_id = s.id
                WHERE n.name = $1
            ),
            deleted AS (
                DELETE FROM namespaces 
                WHERE name = $1 
                RETURNING name
            )
            SELECT 
                deleted.name,
                counts.scope_count,
                counts.knowledge_count
            FROM deleted, counts
        """, name)

        if not result:
            raise ValueError(f"Namespace '{name}' not found")

        log_database_operation("DELETE", query="delete_namespace", params=[name])
        
        return {
            "name": result["name"],
            "scopes_count": result["scope_count"],
            "knowledge_count": result["knowledge_count"]
        }
