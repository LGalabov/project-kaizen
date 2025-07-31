"""MCP tools for namespace management operations."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..database import db_manager
from ..models.namespace import (
    CreateNamespaceInput,
    CreateNamespaceOutput,
    DeleteNamespaceInput,
    DeleteNamespaceOutput,
    GetNamespacesInput,
    GetNamespacesOutput,
    NamespaceInfo,
    NamespaceStyle,
    ScopeInfo,
    UpdateNamespaceInput,
    UpdateNamespaceOutput,
)
from ..utils.logging import (
    log_database_operation,
    log_error_with_context,
    log_mcp_tool_call,
)

# FastMCP server instance
mcp = FastMCP("project-kaizen")


@mcp.tool()
async def get_namespaces(input: GetNamespacesInput) -> GetNamespacesOutput:
    """Discover existing namespaces and scopes to decide whether to create new or reuse existing organizational structures."""
    log_mcp_tool_call("get_namespaces", namespace=input.namespace, style=input.style.value)

    try:
        async with db_manager.acquire() as conn:
            # Base query for namespaces
            namespace_query = "SELECT name, description FROM namespaces"
            params: list[Any] = []

            # Add namespace filter if specified
            if input.namespace:
                namespace_query += " WHERE name = $1"
                params.append(input.namespace)

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
                if input.style != NamespaceStyle.SHORT:
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

            return GetNamespacesOutput(namespaces=namespaces)

    except Exception as e:
        log_error_with_context(e, {"tool": "get_namespaces", "input": input.model_dump()})
        raise


@mcp.tool()
async def create_namespace(input: CreateNamespaceInput) -> CreateNamespaceOutput:
    """Create new namespace with automatic 'default' scope for immediate knowledge storage."""
    log_mcp_tool_call("create_namespace", name=input.name, description=input.description)

    try:
        async with db_manager.acquire() as conn:
            # Create namespace
            namespace_query = """
                INSERT INTO namespaces (name, description)
                VALUES ($1, $2)
                RETURNING id
            """

            log_database_operation("INSERT", query="create_namespace", params=[input.name, input.description])
            namespace_result = await conn.fetchrow(namespace_query, input.name, input.description)

            if not namespace_result:
                raise ValueError(f"Failed to create namespace '{input.name}'")

            namespace_id = namespace_result["id"]

            # Create default scope
            scope_query = """
                INSERT INTO scopes (namespace_id, name, description)
                VALUES ($1, $2, $3)
            """

            default_description = f"{input.description} organization-wide knowledge"
            await conn.execute(scope_query, namespace_id, "default", default_description)

            # Return result with default scope
            scopes: dict[str, ScopeInfo] = {
                "default": ScopeInfo(description=default_description)
            }

            return CreateNamespaceOutput(
                name=input.name,
                description=input.description,
                scopes=scopes
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "create_namespace", "input": input.model_dump()})
        raise


@mcp.tool()
async def update_namespace(input: UpdateNamespaceInput) -> UpdateNamespaceOutput:
    """Update namespace name and/or description with automatic reference updating."""
    log_mcp_tool_call("update_namespace", name=input.name, new_name=input.new_name, description=input.description)

    try:
        async with db_manager.acquire() as conn:
            # Build update query dynamically
            set_clauses: list[str] = []
            params: list[Any] = []
            param_count = 0

            if input.new_name:
                param_count += 1
                set_clauses.append(f"name = ${param_count}")
                params.append(input.new_name)

            if input.description:
                param_count += 1
                set_clauses.append(f"description = ${param_count}")
                params.append(input.description)

            # Always update the updated_at timestamp
            param_count += 1
            set_clauses.append("updated_at = NOW()")

            # Add WHERE clause parameter
            param_count += 1
            params.append(input.name)

            update_query = f"""
                UPDATE namespaces
                SET {', '.join(set_clauses)}
                WHERE name = ${param_count}
                RETURNING name, description
            """

            log_database_operation("UPDATE", query="update_namespace", params=params)
            updated_result = await conn.fetchrow(update_query, *params)

            if not updated_result:
                raise ValueError(f"Namespace '{input.name}' not found")

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
                scopes[scope_row["name"]] = ScopeInfo(
                    description=scope_row["description"]
                )

            return UpdateNamespaceOutput(
                name=updated_result["name"],
                description=updated_result["description"],
                scopes=scopes
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "update_namespace", "input": input.model_dump()})
        raise


@mcp.tool()
async def delete_namespace(input: DeleteNamespaceInput) -> DeleteNamespaceOutput:
    """Remove namespace and all associated scopes and knowledge entries."""
    log_mcp_tool_call("delete_namespace", name=input.name)

    try:
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

            log_database_operation("SELECT", query="delete_namespace_counts", params=[input.name])
            counts_result = await conn.fetchrow(count_query, input.name)

            if counts_result is None:
                raise ValueError(f"Namespace '{input.name}' not found")

            scope_count = counts_result["scope_count"]
            knowledge_count = counts_result["knowledge_count"]

            # Delete namespace (cascades to scopes and knowledge)
            delete_query = """
                DELETE FROM namespaces WHERE name = $1
                RETURNING name
            """

            log_database_operation("DELETE", query="delete_namespace", params=[input.name])
            deleted_result = await conn.fetchrow(delete_query, input.name)

            if not deleted_result:
                raise ValueError(f"Namespace '{input.name}' not found")

            return DeleteNamespaceOutput(
                name=input.name,
                scopes_count=scope_count,
                knowledge_count=knowledge_count
            )

    except Exception as e:
        log_error_with_context(e, {"tool": "delete_namespace", "input": input.model_dump()})
        raise
