"""Project Kaizen MCP Server - Single FastMCP instance with all tools."""

import logging
from typing import Any, Literal

from fastmcp.server import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from mcp.types import ToolAnnotations
from pydantic import Field

# Direct service calls through container - no adapters needed
from .models.knowledge import (
    DeleteKnowledgeOutput,
    GetTaskContextOutput,
    ResolveKnowledgeConflictOutput,
    UpdateKnowledgeOutput,
    WriteKnowledgeOutput,
)
from .types import GLOBAL_DEFAULT_SCOPE, NamespaceStyle, NamespaceStyleLiteral, TaskSize, TaskSizeLiteral
from .models.namespace import (
    CreateNamespaceOutput,
    DeleteNamespaceOutput,
    GetNamespacesOutput,
    UpdateNamespaceOutput,
)
from .models.scope import (
    CreateScopeOutput,
    DeleteScopeOutput,
    UpdateScopeOutput,
)
from .container import get_container
from .utils.mcp import create_tool_result, handle_tool_error
from .utils.logging import log_error_with_context, log_mcp_tool_call

# Set up logging
logger = logging.getLogger("project-kaizen")
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
    logger.info("Starting Project Kaizen MCP Server")
    logger.info(f"Connecting to PostgreSQL: {db_url}")
    logger.info(f"Transport: {transport}")

    # Initialize database through container
    container = get_container()
    try:
        await container.initialize_database(db_url, db_user, db_password, db_name)
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        exit(1)

    logger.info("MCP server ready with database pool")

    # Run the server with the specified transport
    logger.info(f"Starting server with transport: {transport}")
    try:
        match transport:
            case "http":
                logger.info(f"HTTP server starting on {host}:{port}{path}")
                await mcp.run_http_async(
                    host=host, port=port, path=path, stateless_http=True
                )
            case "stdio":
                logger.info("STDIO server starting")
                await mcp.run_stdio_async()
            case _:
                raise ValueError(f"Unsupported transport: {transport}")
    finally:
        # Clean up database pool
        await container.close_resources()


# === MCP SERVER INSTANCE ===

mcp: FastMCP[Any] = FastMCP("project-kaizen")

# === NAMESPACE TOOLS ===


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Namespaces",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def get_namespaces(
    namespace: str | None = Field(
        default=None, description="Optional exact match filter for specific namespace"
    ),
    style: NamespaceStyleLiteral = Field(
        default="short", description="Output detail level: short, long, or details"
    ),
) -> ToolResult:
    """Discover existing namespaces and scopes to decide whether to create new or reuse existing organizational structures."""

    # Convert string to enum
    style_enum = NamespaceStyle(style)

    log_mcp_tool_call("get_namespaces", namespace=namespace, style=style_enum.value)
    try:
        container = get_container()
        service = container.namespace_service()
        namespaces_dict = await service.get_all_namespaces(namespace, style_enum)
        output = GetNamespacesOutput(namespaces=namespaces_dict)
        return create_tool_result(output)
    except Exception as e:
        handle_tool_error(e, "get_namespaces", namespace=namespace, style=style)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Create Namespace",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def create_namespace(
    name: str = Field(
        min_length=2,
        max_length=64,
        pattern=r"^[a-z0-9\-_]+$",
        description="Namespace name (lowercase, alphanumeric, hyphens, underscores)"
    ),
    description: str = Field(
        min_length=2, 
        max_length=64,
        description="Human-readable namespace description"
    ),
) -> ToolResult:
    """Create new namespace with automatic 'default' scope for immediate knowledge storage."""
    log_mcp_tool_call("create_namespace", name=name, description=description)
    
    # Validate description is not empty or whitespace only
    if not description or not description.strip():
        raise ValueError("Description cannot be empty or whitespace only")
    
    try:
        container = get_container()
        service = container.namespace_service()
        result = await service.create_namespace(name, description)
        output = CreateNamespaceOutput(**result)
        return create_tool_result(output)
    except Exception as e:
        handle_tool_error(e, "create_namespace", name=name, description=description)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Update Namespace",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    )
)
async def update_namespace(
    name: str = Field(description="Current namespace name"),
    new_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=64,
        pattern=r"^[a-z0-9\-_]+$", 
        description="New namespace name (optional)"
    ),
    description: str | None = Field(
        default=None,
        min_length=2,
        max_length=64,
        description="Updated namespace description (optional)"
    ),
) -> ToolResult:
    """Update namespace name and/or description with automatic reference updating."""
    
    # Validate description is not empty or whitespace only if provided
    if description is not None and (not description or not description.strip()):
        raise ValueError("Description cannot be empty or whitespace only")
    
    log_mcp_tool_call(
        "update_namespace",
        name=name,
        new_name=new_name,
        description=description,
    )
    try:
        container = get_container()
        service = container.namespace_service()
        result = await service.update_namespace(name, new_name, description)
        output = UpdateNamespaceOutput(**result)
        return create_tool_result(output)
    except Exception as e:
        handle_tool_error(e, "update_namespace", name=name, new_name=new_name, description=description)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Delete Namespace",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def delete_namespace(
    name: str = Field(description="Namespace name to delete"),
) -> ToolResult:
    """Remove namespace and all associated scopes and knowledge entries."""
    log_mcp_tool_call("delete_namespace", name=name)
    try:
        container = get_container()
        service = container.namespace_service()
        result = await service.delete_namespace(name)
        output = DeleteNamespaceOutput(**result)
        return ToolResult(
            content=[TextContent(type="text", text=output.model_dump_json())],
            structured_content=output
        )
    except Exception as e:
        log_error_with_context(e, {"tool": "delete_namespace", "name": name})
        raise


# === SCOPE TOOLS ===


@mcp.tool(
    annotations=ToolAnnotations(
        title="Create Scope",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def create_scope(
    scope: str = Field(
        min_length=5,
        max_length=129,
        description="Full scope identifier (namespace:scope_name)"
    ),
    description: str = Field(
        min_length=2,
        max_length=64,
        description="Human-readable scope description"
    ),
    parents: list[str] | None = Field(
        default=None, description="Optional parent scope identifiers"
    ),
) -> CreateScopeOutput:
    """Create new scope within namespace with automatic 'default' parent inheritance."""
    
    # Validate description is not empty or whitespace only
    if not description or not description.strip():
        raise ValueError("Description cannot be empty or whitespace only")
    
    log_mcp_tool_call(
        "create_scope",
        scope=scope,
        description=description,
        parents=parents,
    )
    try:
        container = get_container()
        service = container.scope_service()
        result = await service.create_scope(scope, description, parents)
        return CreateScopeOutput(**result)
    except Exception as e:
        log_error_with_context(
            e,
            {
                "tool": "create_scope",
                "scope": scope,
                "description": description,
                "parents": parents,
            },
        )
        raise


@mcp.tool(
    annotations=ToolAnnotations(
        title="Update Scope",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    )
)
async def update_scope(
    scope: str = Field(description="Current scope identifier (namespace:scope_name)"),
    new_scope: str | None = Field(
        default=None,
        min_length=5,
        max_length=129,
        description="New scope identifier (optional)"
    ),
    description: str | None = Field(
        default=None,
        min_length=2,
        max_length=64,
        description="Updated scope description (optional)"
    ),
    parents: list[str] | None = Field(
        default=None, description="Updated parent scope identifiers (optional)"
    ),
) -> UpdateScopeOutput:
    """Update scope name, description, and parent relationships with automatic reference updating."""
    
    # Validate description is not empty or whitespace only if provided
    if description is not None and (not description or not description.strip()):
        raise ValueError("Description cannot be empty or whitespace only")
    
    log_mcp_tool_call(
        "update_scope",
        scope=scope,
        new_scope=new_scope,
        description=description,
        parents=parents,
    )
    try:
        container = get_container()
        service = container.scope_service()
        result = await service.update_scope(scope, new_scope, description, parents)
        return UpdateScopeOutput(**result)
    except Exception as e:
        log_error_with_context(
            e,
            {
                "tool": "update_scope",
                "scope": scope,
                "new_scope": new_scope,
                "description": description,
                "parents": parents,
            },
        )
        raise


@mcp.tool(
    annotations=ToolAnnotations(
        title="Delete Scope",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def delete_scope(
    scope: str = Field(description="Scope identifier to delete (namespace:scope_name)"),
) -> DeleteScopeOutput:
    """Remove scope and all associated knowledge entries."""
    log_mcp_tool_call("delete_scope", scope=scope)
    try:
        container = get_container()
        service = container.scope_service()
        result = await service.delete_scope(scope)
        return DeleteScopeOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "delete_scope", "scope": scope})
        raise


# === KNOWLEDGE TOOLS ===


@mcp.tool(
    annotations=ToolAnnotations(
        title="Write Knowledge",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    )
)
async def write_knowledge(
    scope: str = Field(description="Target scope identifier (namespace:scope_name)"),
    content: str = Field(description="Knowledge content to store"),
    context: str = Field(description="Context or summary for the knowledge entry"),
) -> WriteKnowledgeOutput:
    """Store new knowledge entry with automatic scope assignment and context tagging."""
    log_mcp_tool_call(
        "write_knowledge",
        scope=scope,
        content_length=len(content),
        context=context[:50],
    )
    try:
        container = get_container()
        service = container.knowledge_service()
        knowledge_id = await service.create_knowledge_entry(
            scope, content, context
        )
        return WriteKnowledgeOutput(id=knowledge_id, scope=scope)
    except Exception as e:
        log_error_with_context(
            e,
            {
                "tool": "write_knowledge",
                "scope": scope,
                "content_length": len(content),
                "context": context,
            },
        )
        raise


@mcp.tool(
    annotations=ToolAnnotations(
        title="Update Knowledge",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    )
)
async def update_knowledge(
    id: str = Field(description="Knowledge entry ID to update"),
    content: str | None = Field(
        default=None, description="Updated knowledge content (optional)"
    ),
    context: str | None = Field(
        default=None, description="Updated context or summary (optional)"
    ),
    scope: str | None = Field(
        default=None, description="Updated scope identifier (optional)"
    ),
) -> UpdateKnowledgeOutput:
    """Update knowledge entry content, context, or scope assignment."""
    log_mcp_tool_call(
        "update_knowledge",
        id=id,
        content_length=len(content) if content else None,
        scope=scope,
    )
    try:
        container = get_container()
        service = container.knowledge_service()
        final_scope = await service.update_knowledge_entry(
            id, content, context, scope
        )
        return UpdateKnowledgeOutput(id=id, scope=final_scope)
    except Exception as e:
        log_error_with_context(
            e,
            {
                "tool": "update_knowledge",
                "id": id,
                "content_length": len(content) if content else None,
                "scope": scope,
            },
        )
        raise


@mcp.tool(
    annotations=ToolAnnotations(
        title="Delete Knowledge",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def delete_knowledge(
    id: str = Field(description="Knowledge entry ID to delete"),
) -> DeleteKnowledgeOutput:
    """Remove knowledge entry from system."""
    log_mcp_tool_call("delete_knowledge", id=id)
    try:
        container = get_container()
        service = container.knowledge_service()
        deleted_id = await service.delete_knowledge_entry(id)
        return DeleteKnowledgeOutput(id=deleted_id)
    except Exception as e:
        log_error_with_context(e, {"tool": "delete_knowledge", "id": id})
        raise


@mcp.tool(
    annotations=ToolAnnotations(
        title="Resolve Knowledge Conflict",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def resolve_knowledge_conflict(
    active_id: str = Field(description="Knowledge entry ID to keep as active"),
    suppressed_ids: list[str] = Field(
        description="Knowledge entry IDs to suppress due to conflict"
    ),
) -> ResolveKnowledgeConflictOutput:
    """Mark knowledge entries for conflict resolution when contradictory information exists."""
    log_mcp_tool_call(
        "resolve_knowledge_conflict",
        active_id=active_id,
        suppressed_count=len(suppressed_ids),
    )
    try:
        container = get_container()
        service = container.knowledge_service()
        (
            resolved_active_id,
            resolved_suppressed_ids,
        ) = await service.resolve_knowledge_conflicts(active_id, suppressed_ids)
        return ResolveKnowledgeConflictOutput(
            active_id=resolved_active_id, suppressed_ids=resolved_suppressed_ids
        )
    except Exception as e:
        log_error_with_context(
            e,
            {
                "tool": "resolve_knowledge_conflict",
                "active_id": active_id,
                "suppressed_ids": suppressed_ids,
            },
        )
        raise


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Task Context",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def get_task_context(
    queries: list[str] = Field(
        description="Multiple targeted search queries for the task"
    ),
    scope: str | None = Field(
        default=None,
        description="Optional scope to limit search (namespace:scope_name)",
    ),
    task_size: TaskSizeLiteral | None = Field(
        default=None, description="Task complexity: XS, S, M, L, or XL"
    ),
) -> GetTaskContextOutput:
    """AI provides multiple targeted queries for complex tasks, MCP returns relevant knowledge organized by scope hierarchy."""

    # Convert string to enum if provided
    task_size_enum = TaskSize(task_size) if task_size else None

    log_mcp_tool_call(
        "get_task_context",
        queries=queries,
        scope=scope,
        task_size=task_size_enum.value if task_size_enum else None,
    )
    try:
        task_size_value = task_size_enum.value if task_size_enum else None
        # get_task_context_knowledge requires scope to be non-None, provide default
        effective_scope = scope or GLOBAL_DEFAULT_SCOPE
        container = get_container()
        service = container.knowledge_service()
        results = await service.get_task_context_knowledge(
            queries, effective_scope, task_size_value
        )
        return GetTaskContextOutput(results=results)
    except Exception as e:
        log_error_with_context(
            e,
            {
                "tool": "get_task_context",
                "queries": queries,
                "scope": scope,
                "task_size": task_size,
            },
        )
        raise
