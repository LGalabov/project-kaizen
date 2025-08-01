"""Project Kaizen MCP Server - Single FastMCP instance with all tools."""

import logging
from typing import Any, Literal

import asyncpg
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .core import knowledge_ops, namespace_ops, scope_ops
from .models.knowledge import (
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
from .models.namespace import (
    CreateNamespaceInput,
    CreateNamespaceOutput,
    DeleteNamespaceInput,
    DeleteNamespaceOutput,
    GetNamespacesInput,
    GetNamespacesOutput,
    UpdateNamespaceInput,
    UpdateNamespaceOutput,
)
from .models.scope import (
    CreateScopeInput,
    CreateScopeOutput,
    DeleteScopeInput,
    DeleteScopeOutput,
    UpdateScopeInput,
    UpdateScopeOutput,
)
from .utils.logging import log_error_with_context, log_mcp_tool_call

# Set up logging
logger = logging.getLogger('project-kaizen')
logger.setLevel(logging.INFO)


async def main(
    db_url: str,
    db_user: str, 
    db_password: str,
    db_name: str,
    transport: Literal["stdio", "http"] = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp/",
) -> None:
    """Main entry point for the MCP server."""
    logger.info(f"Starting Project Kaizen MCP Server")
    logger.info(f"Connecting to PostgreSQL: {db_url}")
    logger.info(f"Transport: {transport}")

    # Build connection URL if components provided, otherwise use db_url directly
    if db_url.startswith('postgresql://'):
        connection_url = db_url
    else:
        # Assume db_url is host, build full URL
        connection_url = f"postgresql://{db_user}:{db_password}@{db_url}/{db_name}"
    
    # Create connection pool
    try:
        pool = await asyncpg.create_pool(
            connection_url,
            min_size=1,
            max_size=2
        )
        logger.info(f"Connected to PostgreSQL pool: {connection_url.split('@')[0]}@{connection_url.split('@')[1]}")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        exit(1)

    # Verify connection with a simple query
    try:
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        await pool.close()
        exit(1)
    
    logger.info("MCP server ready with database pool")
    
    # Run the server with the specified transport
    logger.info(f"Starting server with transport: {transport}")
    try:
        match transport:
            case "http":
                logger.info(f"HTTP server starting on {host}:{port}{path}")
                await mcp.run_http_async(host=host, port=port, path=path, stateless_http=True)
            case "stdio":
                logger.info("STDIO server starting")
                await mcp.run_stdio_async()
            case _:
                raise ValueError(f"Unsupported transport: {transport}")
    finally:
        # Clean up database pool
        await pool.close()
        logger.info("Database pool closed")


# === MCP SERVER INSTANCE ===

mcp: FastMCP[Any] = FastMCP("project-kaizen")

# === NAMESPACE TOOLS ===


@mcp.tool(annotations=ToolAnnotations(
    title="Get Namespaces",
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True
))
async def get_namespaces(input: GetNamespacesInput) -> GetNamespacesOutput:
    """Discover existing namespaces and scopes to decide whether to create new or reuse existing organizational structures."""
    log_mcp_tool_call(
        "get_namespaces", namespace=input.namespace, style=input.style.value
    )
    try:
        result = await namespace_ops.list_namespaces(input.namespace, input.style)
        return GetNamespacesOutput(namespaces=result)
    except Exception as e:
        log_error_with_context(
            e, {"tool": "get_namespaces", "input": input.model_dump()}
        )
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Create Namespace",
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True
))
async def create_namespace(input: CreateNamespaceInput) -> CreateNamespaceOutput:
    """Create new namespace with automatic 'default' scope for immediate knowledge storage."""
    log_mcp_tool_call(
        "create_namespace", name=input.name, description=input.description
    )
    try:
        result = await namespace_ops.create_namespace(input.name, input.description)
        return CreateNamespaceOutput(**result)
    except Exception as e:
        log_error_with_context(
            e, {"tool": "create_namespace", "input": input.model_dump()}
        )
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Update Namespace",
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True
))
async def update_namespace(input: UpdateNamespaceInput) -> UpdateNamespaceOutput:
    """Update namespace name and/or description with automatic reference updating."""
    log_mcp_tool_call(
        "update_namespace",
        name=input.name,
        new_name=input.new_name,
        description=input.description,
    )
    try:
        result = await namespace_ops.update_namespace(
            input.name, input.new_name, input.description
        )
        return UpdateNamespaceOutput(**result)
    except Exception as e:
        log_error_with_context(
            e, {"tool": "update_namespace", "input": input.model_dump()}
        )
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Delete Namespace", 
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True
))
async def delete_namespace(input: DeleteNamespaceInput) -> DeleteNamespaceOutput:
    """Remove namespace and all associated scopes and knowledge entries."""
    log_mcp_tool_call("delete_namespace", name=input.name)
    try:
        result = await namespace_ops.delete_namespace(input.name)
        return DeleteNamespaceOutput(**result)
    except Exception as e:
        log_error_with_context(
            e, {"tool": "delete_namespace", "input": input.model_dump()}
        )
        raise


# === SCOPE TOOLS ===


@mcp.tool(annotations=ToolAnnotations(
    title="Create Scope",
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True
))
async def create_scope(input: CreateScopeInput) -> CreateScopeOutput:
    """Create new scope within namespace with automatic 'default' parent inheritance."""
    log_mcp_tool_call(
        "create_scope",
        scope=input.scope,
        description=input.description,
        parents=input.parents,
    )
    try:
        namespace_name, scope_name = input.scope.split(":", 1)
        result = await scope_ops.create_scope(
            namespace_name, scope_name, input.description, input.parents
        )
        return CreateScopeOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "create_scope", "input": input.model_dump()})
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Update Scope",
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True
))
async def update_scope(input: UpdateScopeInput) -> UpdateScopeOutput:
    """Update scope name, description, and parent relationships with automatic reference updating."""
    log_mcp_tool_call(
        "update_scope",
        scope=input.scope,
        new_scope=input.new_scope,
        description=input.description,
        parents=input.parents,
    )
    try:
        result = await scope_ops.update_scope(
            input.scope, input.new_scope, input.description, input.parents
        )
        return UpdateScopeOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "update_scope", "input": input.model_dump()})
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Delete Scope",
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True
))
async def delete_scope(input: DeleteScopeInput) -> DeleteScopeOutput:
    """Remove scope and all associated knowledge entries."""
    log_mcp_tool_call("delete_scope", scope=input.scope)
    try:
        result = await scope_ops.delete_scope(input.scope)
        return DeleteScopeOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "delete_scope", "input": input.model_dump()})
        raise


# === KNOWLEDGE TOOLS ===


@mcp.tool(annotations=ToolAnnotations(
    title="Write Knowledge",
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True
))
async def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
    """Store new knowledge entry with automatic scope assignment and context tagging."""
    log_mcp_tool_call(
        "write_knowledge",
        scope=input.scope,
        content_length=len(input.content),
        context=input.context[:50],
    )
    try:
        knowledge_id = await knowledge_ops.create_knowledge_entry(
            input.scope, input.content, input.context
        )
        return WriteKnowledgeOutput(id=knowledge_id, scope=input.scope)
    except Exception as e:
        log_error_with_context(
            e, {"tool": "write_knowledge", "input": input.model_dump()}
        )
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Update Knowledge",
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True
))
async def update_knowledge(input: UpdateKnowledgeInput) -> UpdateKnowledgeOutput:
    """Update knowledge entry content, context, or scope assignment."""
    log_mcp_tool_call(
        "update_knowledge",
        id=input.id,
        content_length=len(input.content) if input.content else None,
        scope=input.scope,
    )
    try:
        final_scope = await knowledge_ops.update_knowledge_entry(
            input.id, input.content, input.context, input.scope
        )
        return UpdateKnowledgeOutput(id=input.id, scope=final_scope)
    except Exception as e:
        log_error_with_context(
            e, {"tool": "update_knowledge", "input": input.model_dump()}
        )
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Delete Knowledge",
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True
))
async def delete_knowledge(input: DeleteKnowledgeInput) -> DeleteKnowledgeOutput:
    """Remove knowledge entry from system."""
    log_mcp_tool_call("delete_knowledge", id=input.id)
    try:
        deleted_id = await knowledge_ops.delete_knowledge_entry(input.id)
        return DeleteKnowledgeOutput(id=deleted_id)
    except Exception as e:
        log_error_with_context(
            e, {"tool": "delete_knowledge", "input": input.model_dump()}
        )
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Resolve Knowledge Conflict",
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True
))
async def resolve_knowledge_conflict(
    input: ResolveKnowledgeConflictInput,
) -> ResolveKnowledgeConflictOutput:
    """Mark knowledge entries for conflict resolution when contradictory information exists."""
    log_mcp_tool_call(
        "resolve_knowledge_conflict",
        active_id=input.active_id,
        suppressed_count=len(input.suppressed_ids),
    )
    try:
        active_id, suppressed_ids = await knowledge_ops.resolve_knowledge_conflicts(
            input.active_id, input.suppressed_ids
        )
        return ResolveKnowledgeConflictOutput(
            active_id=active_id, suppressed_ids=suppressed_ids
        )
    except Exception as e:
        log_error_with_context(
            e, {"tool": "resolve_knowledge_conflict", "input": input.model_dump()}
        )
        raise


@mcp.tool(annotations=ToolAnnotations(
    title="Get Task Context", 
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True
))
async def get_task_context(input: GetTaskContextInput) -> GetTaskContextOutput:
    """AI provides multiple targeted queries for complex tasks, MCP returns relevant knowledge organized by scope hierarchy."""
    log_mcp_tool_call(
        "get_task_context",
        queries=input.queries,
        scope=input.scope,
        task_size=input.task_size.value if input.task_size else None,
    )
    try:
        task_size_value = input.task_size.value if input.task_size else None
        results = await knowledge_ops.get_task_context_knowledge(
            input.queries, input.scope, task_size_value
        )
        return GetTaskContextOutput(results=results)
    except Exception as e:
        log_error_with_context(
            e, {"tool": "get_task_context", "input": input.model_dump()}
        )
        raise
