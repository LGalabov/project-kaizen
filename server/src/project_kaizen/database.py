"""Database operations for Project Kaizen MCP Server."""

import sys
from typing import Any

import asyncpg

from project_kaizen.config import Config
from project_kaizen.utils import parse_canonical_scope_name

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get the database connection pool."""
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call initialize() first.")
    return _pool


async def initialize(config: Config) -> None:
    """Initialize the database connection pool."""
    global _pool
    
    try:
        _pool = await asyncpg.create_pool(
            config.database_url,
            min_size=config.database_pool_min,
            max_size=config.database_pool_max,
            command_timeout=60,
        )
        print("✓ Database connected", file=sys.stderr)
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}", file=sys.stderr)
        sys.exit(1)


# ============================================================================
# Namespace operations
# ============================================================================


async def create_namespace(namespace_name: str, description: str) -> dict[str, Any]:
    """Create namespace with automatic default scope."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO namespaces (name, description) VALUES ($1, $2)",
                namespace_name,
                description,
            )

            return {
                "namespace": namespace_name,
                "description": description,
                "default_scope": f"{namespace_name}:default",
            }


async def list_namespaces() -> dict[str, Any]:
    """List all namespaces with their scopes and parent relationships."""
    return await _get_namespaces_data()


async def get_namespace_details(namespace_name: str) -> dict[str, Any]:
    """Get complete details for a specific namespace including all scopes and parent relationships."""
    data = await _get_namespaces_data(namespace_name)

    if namespace_name not in data["namespaces"]:
        raise ValueError(f"Namespace '{namespace_name}' not found")

    ns_data = data["namespaces"][namespace_name]
    canonical_scopes = [f"{namespace_name}:{scope_name}" for scope_name in ns_data["scopes"].keys()]
    
    return {"namespace": namespace_name, "description": ns_data["description"], "scopes": canonical_scopes}


async def rename_namespace(old_namespace_name: str, new_namespace_name: str) -> dict[str, Any]:
    """Rename a namespace (all references auto-updated via cascade)."""
    if old_namespace_name == "global":
        raise ValueError("Cannot rename the global namespace")
    
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            result = await conn.fetchrow(
                """UPDATE namespaces 
                   SET name = $2, updated_at = NOW()
                   WHERE name = $1
                   RETURNING description""",
                old_namespace_name,
                new_namespace_name,
            )

            if not result:
                raise ValueError(f"Namespace '{old_namespace_name}' not found")

            return {
                "namespace": new_namespace_name,
                "description": result["description"],
                "previous_name": old_namespace_name,
            }


async def update_namespace_description(namespace_name: str, new_description: str) -> dict[str, Any]:
    """Update namespace description only."""
    if namespace_name == "global":
        raise ValueError("Cannot modify the global namespace description")
    
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """UPDATE namespaces 
               SET description = $2, updated_at = NOW()
               WHERE name = $1
               RETURNING name""",
            namespace_name,
            new_description,
        )

        if not result:
            raise ValueError(f"Namespace '{namespace_name}' not found")

        return {"namespace": namespace_name, "description": new_description}


async def delete_namespace(namespace_name: str) -> dict[str, Any]:
    """Delete namespace and ALL associated data (cannot be undone)."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(DISTINCT s.id) as scopes_count,
                    COUNT(DISTINCT k.id) as knowledge_count
                FROM namespaces n
                LEFT JOIN scopes s ON n.id = s.namespace_id
                LEFT JOIN knowledge k ON s.id = k.scope_id
                WHERE n.name = $1
                GROUP BY n.id
            """,
                namespace_name,
            )

            if not stats:
                raise ValueError(f"Namespace '{namespace_name}' not found")

            await conn.execute("DELETE FROM namespaces WHERE name = $1", namespace_name)

            return {
                "namespace": namespace_name,
                "deleted_scopes": stats["scopes_count"] or 0,
                "deleted_knowledge": stats["knowledge_count"] or 0,
            }


# ============================================================================
# Scope operations
# ============================================================================


async def create_scope(canonical_scope_name: str, description: str, parents: list[str]) -> dict[str, Any]:
    """Create a new scope with specified parent relationships."""
    namespace_name, scope_name = parse_canonical_scope_name(canonical_scope_name)
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            ns_id = await conn.fetchval("SELECT id FROM namespaces WHERE name = $1", namespace_name)

            if not ns_id:
                raise ValueError(f"Namespace '{namespace_name}' not found")

            await conn.execute(
                """INSERT INTO scopes (namespace_id, name, description)
                   VALUES ($1, $2, $3)""",
                ns_id,
                scope_name,
                description,
            )

            # Add any additional parents using the database function
            final_parents = await conn.fetchval(
                "SELECT add_scope_parents($1, $2)", canonical_scope_name, parents if parents else []
            )

            return {"scope": canonical_scope_name, "description": description, "parents": final_parents or []}


async def rename_scope(canonical_scope_name: str, new_scope_name: str) -> dict[str, Any]:
    """Rename a scope within the same namespace (references auto-updated)."""
    namespace_name, old_scope_name = parse_canonical_scope_name(canonical_scope_name)
    
    if old_scope_name == "default":
        raise ValueError("Cannot rename default scope")
    
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            result = await conn.fetchrow(
                """UPDATE scopes 
                   SET name = $3, updated_at = NOW()
                   FROM namespaces n
                   WHERE scopes.namespace_id = n.id 
                     AND n.name = $1 
                     AND scopes.name = $2
                   RETURNING scopes.description""",
                namespace_name,
                old_scope_name,
                new_scope_name,
            )

            if not result:
                raise ValueError(f"Scope '{canonical_scope_name}' not found")

            return {
                "scope": f"{namespace_name}:{new_scope_name}",
                "previous_name": canonical_scope_name,
                "description": result["description"],
            }


async def update_scope_description(canonical_scope_name: str, new_description: str) -> dict[str, Any]:
    """Update scope description only."""
    if canonical_scope_name == "global:default":
        raise ValueError("Cannot modify the global:default scope description")
    
    namespace_name, scope_name = parse_canonical_scope_name(canonical_scope_name)
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """UPDATE scopes 
               SET description = $3, updated_at = NOW()
               FROM namespaces n
               WHERE scopes.namespace_id = n.id 
                 AND n.name = $1 
                 AND scopes.name = $2
               RETURNING scopes.name""",
            namespace_name,
            scope_name,
            new_description,
        )

        if not result:
            raise ValueError(f"Scope '{canonical_scope_name}' not found")

        return {"scope": canonical_scope_name, "description": new_description}


async def add_scope_parents(canonical_scope_name: str, parent_canonical_scope_names: list[str]) -> dict[str, Any]:
    """Add parent relationships to an existing scope."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        final_parents = await conn.fetchval(
            "SELECT add_scope_parents($1, $2)", canonical_scope_name, parent_canonical_scope_names
        )

        if final_parents is None:
            raise ValueError(f"Scope '{canonical_scope_name}' not found")

        return {
            "scope": canonical_scope_name,
            "added_parents": parent_canonical_scope_names,
            "parents": final_parents,
        }


async def remove_scope_parents(canonical_scope_name: str, parent_canonical_scope_names: list[str]) -> dict[str, Any]:
    """Remove parent relationships from a scope."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        remaining_parents = await conn.fetchval(
            "SELECT remove_scope_parents($1, $2)", canonical_scope_name, parent_canonical_scope_names
        )

        if remaining_parents is None:
            # Check if the scope exists to provide a better error message
            scope_exists = await conn.fetchval(
                """SELECT EXISTS(
                    SELECT 1 FROM scopes s
                    JOIN namespaces n ON s.namespace_id = n.id
                    WHERE n.name || ':' || s.name = $1
                )""",
                canonical_scope_name,
            )
            if not scope_exists:
                raise ValueError(f"Scope '{canonical_scope_name}' not found")
            else:
                raise ValueError("One or more parent scopes not found or not parents of this scope")

        return {
            "scope": canonical_scope_name,
            "removed_parents": parent_canonical_scope_names,
            "parents": remaining_parents or [],
        }


async def delete_scope(canonical_scope_name: str) -> dict[str, Any]:
    """Delete scope and ALL associated knowledge (cannot delete default scopes)."""
    namespace_name, scope_name = parse_canonical_scope_name(canonical_scope_name)
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            if scope_name == "default":
                raise ValueError("Cannot delete default scope")

            stats = await conn.fetchrow(
                """
                SELECT COUNT(k.id) as knowledge_count
                FROM scopes s
                JOIN namespaces n ON s.namespace_id = n.id
                LEFT JOIN knowledge k ON s.id = k.scope_id
                WHERE n.name = $1 AND s.name = $2
                GROUP BY s.id
            """,
                namespace_name,
                scope_name,
            )

            if not stats:
                raise ValueError(f"Scope '{canonical_scope_name}' not found")

            await conn.execute(
                """
                DELETE FROM scopes 
                USING namespaces n
                WHERE scopes.namespace_id = n.id 
                  AND n.name = $1 
                  AND scopes.name = $2
            """,
                namespace_name,
                scope_name,
            )

            return {"scope": canonical_scope_name, "knowledge_deleted": stats["knowledge_count"] or 0}


# ============================================================================
# Knowledge operations
# ============================================================================


async def write_knowledge(
        canonical_scope_name: str, content: str, context: str, task_size: str | None
) -> dict[str, Any]:
    """Store new knowledge entry with optional task size classification."""
    namespace_name, scope_name = parse_canonical_scope_name(canonical_scope_name)
    pool = await get_pool()

    async with pool.acquire() as conn:
        knowledge_id = await conn.fetchval(
            """
            INSERT INTO knowledge (scope_id, content, context, task_size)
            SELECT s.id, $3, $4, $5
            FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE n.name = $1 AND s.name = $2
            RETURNING id
        """,
            namespace_name,
            scope_name,
            content,
            context,
            task_size,
        )

        if knowledge_id is None:
            raise ValueError(f"Scope '{canonical_scope_name}' not found")

        return {"id": knowledge_id, "scope": canonical_scope_name}


async def update_knowledge_content(knowledge_id: int, new_content: str) -> dict[str, Any]:
    """Update the content of an existing knowledge entry."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """UPDATE knowledge 
               SET content = $2, updated_at = NOW()
               WHERE id = $1
               RETURNING id""",
            knowledge_id,
            new_content,
        )

        if not result:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        return {"id": knowledge_id}


async def update_knowledge_context(knowledge_id: int, new_context: str) -> dict[str, Any]:
    """Update the context/summary of a knowledge entry."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """UPDATE knowledge 
               SET context = $2, updated_at = NOW()
               WHERE id = $1
               RETURNING id""",
            knowledge_id,
            new_context,
        )

        if not result:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        return {"id": knowledge_id}


async def move_knowledge_to_scope(knowledge_id: int, new_canonical_scope_name: str) -> dict[str, Any]:
    """Move knowledge entry to a different scope."""
    namespace_name, scope_name = parse_canonical_scope_name(new_canonical_scope_name)
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """
            UPDATE knowledge 
            SET scope_id = s.id, updated_at = NOW()
            FROM scopes s
            JOIN namespaces n ON s.namespace_id = n.id
            WHERE knowledge.id = $1
              AND n.name = $2 
              AND s.name = $3
            RETURNING knowledge.id
        """,
            knowledge_id,
            namespace_name,
            scope_name,
        )

        if not result:
            knowledge_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM knowledge WHERE id = $1)", knowledge_id)
            if not knowledge_exists:
                raise ValueError(f"Knowledge entry {knowledge_id} not found")
            else:
                raise ValueError(f"Scope '{new_canonical_scope_name}' not found")

        return {"id": knowledge_id, "new_scope": new_canonical_scope_name}


async def update_knowledge_task_size(knowledge_id: int, new_task_size: str) -> dict[str, Any]:
    """Update task size classification for a knowledge entry."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """UPDATE knowledge 
               SET task_size = $2, updated_at = NOW()
               WHERE id = $1
               RETURNING id""",
            knowledge_id,
            new_task_size,
        )

        if not result:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        return {"id": knowledge_id, "task_size": new_task_size}


async def delete_knowledge(knowledge_id: int) -> dict[str, Any]:
    """Remove knowledge entry from the system (cannot be undone)."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        deleted = await conn.execute("DELETE FROM knowledge WHERE id = $1", knowledge_id)

        if "DELETE 0" in deleted:
            raise ValueError(f"Knowledge entry {knowledge_id} not found")

        return {"id": knowledge_id}


async def resolve_knowledge_conflict(active_knowledge_id: int, suppressed_knowledge_ids: list[int]) -> dict[str, Any]:
    """Mark knowledge entries for conflict resolution when contradictory information exists."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            all_ids = [active_knowledge_id] + suppressed_knowledge_ids
            existing_ids = await conn.fetch("SELECT id FROM knowledge WHERE id = ANY($1)", all_ids)

            if len(existing_ids) != len(all_ids):
                found_ids = {row["id"] for row in existing_ids}
                missing_ids = set(all_ids) - found_ids
                raise ValueError(f"Knowledge entries not found: {missing_ids}")

            await conn.execute(
                """INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids)
                   VALUES ($1, $2)""",
                active_knowledge_id,
                suppressed_knowledge_ids,
            )

            return {"active_id": active_knowledge_id, "suppressed_ids": suppressed_knowledge_ids}


# ============================================================================
# Knowledge base search operations
# ============================================================================


async def search_knowledge_base(
    queries: list[str], canonical_scope_name: str, task_size: str | None
) -> list[str]:
    """Search knowledge base using multiple queries within the scope hierarchy."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM search_knowledge_base($1, $2, $3)", queries, canonical_scope_name, task_size
        )

        # Format as "ID: content" strings, already sorted by rank DESC
        return [f"{row['knowledge_id']}: {row['content']}" for row in rows]


# ============================================================================
# Configuration operations
# ============================================================================


async def list_config() -> dict[str, Any]:
    """Get all configuration settings."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT key, value, default_value, value_type, description
            FROM config
            ORDER BY key
        """)

        result: dict[str, dict[str, Any]] = {"configs": {}}
        for row in rows:
            result["configs"][row["key"]] = {
                "value": row["value"],
                "default": row["default_value"],
                "type": row["value_type"],
                "description": row["description"],
            }

        return result


async def update_config(key: str, value: str) -> dict[str, Any]:
    """Update a configuration value with comprehensive validation."""
    if not key or not key.strip():
        raise ValueError("Configuration key cannot be empty")
    
    if value is None:
        raise ValueError("Configuration value cannot be None")
    
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Get current config details
            config_row = await conn.fetchrow(
                "SELECT value, value_type, description FROM config WHERE key = $1", key
            )

            if not config_row:
                raise ValueError(f"Configuration key '{key}' not found")

            old_value = config_row["value"]
            value_type = config_row["value_type"]
            
            # Validate the new value matches the expected type
            try:
                if value_type == "integer":
                    int(value)
                elif value_type == "float":
                    float(value)
                elif value_type == "boolean":
                    if value.lower() not in ("true", "false"):
                        raise ValueError("Boolean values must be 'true' or 'false'")
                elif value_type == "regconfig":
                    # Test if it's a valid regconfig by trying to cast it
                    await conn.fetchval("SELECT $1::regconfig", value)
                # 'text' type accepts any string value
            except (ValueError, TypeError) as e:
                raise ValueError(f"Configuration value '{value}' is invalid for type '{value_type}': {e}") from e
            except Exception as e:
                raise ValueError(f"Configuration value '{value}' is invalid for type '{value_type}'") from e

            # Update the configuration (bypassing the database function)
            await conn.execute(
                "UPDATE config SET value = $2, updated_at = NOW() WHERE key = $1", 
                key, value
            )

            return {"key": key, "old_value": old_value, "new_value": value}


async def reset_config(key: str) -> dict[str, Any]:
    """Reset a configuration to default."""
    if not key or not key.strip():
        raise ValueError("Configuration key cannot be empty")
        
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Get the default value and reset
            config_row = await conn.fetchrow(
                "SELECT default_value FROM config WHERE key = $1", key
            )
            
            if not config_row:
                raise ValueError(f"Configuration key '{key}' not found")
                
            default_value = config_row["default_value"]
            
            # Update to default value
            await conn.execute(
                "UPDATE config SET value = default_value, updated_at = NOW() WHERE key = $1",
                key
            )

            return {"key": key, "value": default_value}


# ============================================================================
# Helper functions
# ============================================================================


async def _get_namespaces_data(namespace_name: str | None = None) -> dict[str, Any]:
    """Internal function to get namespace data with optional filtering."""
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Query 1: Get namespaces with scopes (single query handles both cases)
        rows = await conn.fetch(
            """
            SELECT n.name as namespace_name, n.description as namespace_description,
                   s.name as scope_name, s.description as scope_description
            FROM namespaces n
            LEFT JOIN scopes s ON n.id = s.namespace_id
            WHERE $1::text IS NULL OR n.name = $1
            ORDER BY n.name, s.name
        """,
            namespace_name,
        )

        if not rows:
            return {"namespaces": {}}

        # Query 2: Get parent relationships (single query handles both cases)
        parents = await conn.fetch(
            """
            SELECT n.name || ':' || s.name as child_scope,
                   pn.name || ':' || ps.name as parent_scope
            FROM scope_parents sp
            JOIN scopes s ON sp.child_scope_id = s.id
            JOIN namespaces n ON s.namespace_id = n.id
            JOIN scopes ps ON sp.parent_scope_id = ps.id
            JOIN namespaces pn ON ps.namespace_id = pn.id
            WHERE $1::text IS NULL OR n.name = $1
        """,
            namespace_name,
        )

        # Build parent lookup
        parent_map: dict[str, list[str]] = {}
        for p in parents:
            if p["child_scope"] not in parent_map:
                parent_map[p["child_scope"]] = []
            parent_map[p["child_scope"]].append(p["parent_scope"])

        # Build result structure
        result: dict[str, dict[str, Any]] = {"namespaces": {}}
        for row in rows:
            ns_name = row["namespace_name"]
            if ns_name not in result["namespaces"]:
                result["namespaces"][ns_name] = {"description": row["namespace_description"], "scopes": {}}

            if row["scope_name"]:
                scope_key = f"{ns_name}:{row['scope_name']}"
                result["namespaces"][ns_name]["scopes"][row["scope_name"]] = {
                    "description": row["scope_description"],
                    "parents": parent_map.get(scope_key, []),
                }

        return result
