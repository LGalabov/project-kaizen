"""Project Kaizen MCP Server - Single FastMCP instance with all tools."""

from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP

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
from .core import knowledge_ops, namespace_ops, scope_ops
from .utils.logging import get_logger, log_mcp_tool_call, log_error_with_context

# Single global FastMCP instance
mcp = FastMCP("project-kaizen")

# === NAMESPACE TOOLS ===

@mcp.tool
async def get_namespaces(input: GetNamespacesInput) -> GetNamespacesOutput:
    """Discover existing namespaces and scopes to decide whether to create new or reuse existing organizational structures."""
    log_mcp_tool_call("get_namespaces", namespace=input.namespace, style=input.style.value)
    try:
        result = await namespace_ops.list_namespaces(input.namespace, input.style)
        return GetNamespacesOutput(namespaces=result)
    except Exception as e:
        log_error_with_context(e, {"tool": "get_namespaces", "input": input.model_dump()})
        raise


@mcp.tool
async def create_namespace(input: CreateNamespaceInput) -> CreateNamespaceOutput:
    """Create new namespace with automatic 'default' scope for immediate knowledge storage."""
    log_mcp_tool_call("create_namespace", name=input.name, description=input.description)
    try:
        result = await namespace_ops.create_namespace(input.name, input.description)
        return CreateNamespaceOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "create_namespace", "input": input.model_dump()})
        raise


@mcp.tool
async def update_namespace(input: UpdateNamespaceInput) -> UpdateNamespaceOutput:
    """Update namespace name and/or description with automatic reference updating."""
    log_mcp_tool_call("update_namespace", name=input.name, new_name=input.new_name, description=input.description)
    try:
        result = await namespace_ops.update_namespace(input.name, input.new_name, input.description)
        return UpdateNamespaceOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "update_namespace", "input": input.model_dump()})
        raise


@mcp.tool
async def delete_namespace(input: DeleteNamespaceInput) -> DeleteNamespaceOutput:
    """Remove namespace and all associated scopes and knowledge entries."""
    log_mcp_tool_call("delete_namespace", name=input.name)
    try:
        result = await namespace_ops.delete_namespace(input.name)
        return DeleteNamespaceOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "delete_namespace", "input": input.model_dump()})
        raise

# === SCOPE TOOLS ===

@mcp.tool
async def create_scope(input: CreateScopeInput) -> CreateScopeOutput:
    """Create new scope within namespace with automatic 'default' parent inheritance."""
    log_mcp_tool_call("create_scope", scope=input.scope, description=input.description, parents=input.parents)
    try:
        namespace_name, scope_name = input.scope.split(":", 1)
        result = await scope_ops.create_scope(namespace_name, scope_name, input.description, input.parents)
        return CreateScopeOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "create_scope", "input": input.model_dump()})
        raise


@mcp.tool
async def update_scope(input: UpdateScopeInput) -> UpdateScopeOutput:
    """Update scope name, description, and parent relationships with automatic reference updating."""
    log_mcp_tool_call("update_scope", scope=input.scope, new_scope=input.new_scope, description=input.description, parents=input.parents)
    try:
        result = await scope_ops.update_scope(input.scope, input.new_scope, input.description, input.parents)
        return UpdateScopeOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "update_scope", "input": input.model_dump()})
        raise


@mcp.tool
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

@mcp.tool
async def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
    """Store new knowledge entry with automatic scope assignment and context tagging."""
    log_mcp_tool_call("write_knowledge", scope=input.scope, content_length=len(input.content), context=input.context[:50])
    try:
        knowledge_id = await knowledge_ops.create_knowledge_entry(input.scope, input.content, input.context)
        return WriteKnowledgeOutput(id=knowledge_id, scope=input.scope)
    except Exception as e:
        log_error_with_context(e, {"tool": "write_knowledge", "input": input.model_dump()})
        raise


@mcp.tool
async def update_knowledge(input: UpdateKnowledgeInput) -> UpdateKnowledgeOutput:
    """Update knowledge entry content, context, or scope assignment."""
    log_mcp_tool_call("update_knowledge", id=input.id, content_length=len(input.content) if input.content else None, scope=input.scope)
    try:
        final_scope = await knowledge_ops.update_knowledge_entry(input.id, input.content, input.context, input.scope)
        return UpdateKnowledgeOutput(id=input.id, scope=final_scope)
    except Exception as e:
        log_error_with_context(e, {"tool": "update_knowledge", "input": input.model_dump()})
        raise


@mcp.tool
async def delete_knowledge(input: DeleteKnowledgeInput) -> DeleteKnowledgeOutput:
    """Remove knowledge entry from system."""
    log_mcp_tool_call("delete_knowledge", id=input.id)
    try:
        deleted_id = await knowledge_ops.delete_knowledge_entry(input.id)
        return DeleteKnowledgeOutput(id=deleted_id)
    except Exception as e:
        log_error_with_context(e, {"tool": "delete_knowledge", "input": input.model_dump()})
        raise


@mcp.tool
async def resolve_knowledge_conflict(input: ResolveKnowledgeConflictInput) -> ResolveKnowledgeConflictOutput:
    """Mark knowledge entries for conflict resolution when contradictory information exists."""
    log_mcp_tool_call("resolve_knowledge_conflict", active_id=input.active_id, suppressed_count=len(input.suppressed_ids))
    try:
        active_id, suppressed_ids = await knowledge_ops.resolve_knowledge_conflicts(input.active_id, input.suppressed_ids)
        return ResolveKnowledgeConflictOutput(active_id=active_id, suppressed_ids=suppressed_ids)
    except Exception as e:
        log_error_with_context(e, {"tool": "resolve_knowledge_conflict", "input": input.model_dump()})
        raise


@mcp.tool
async def get_task_context(input: GetTaskContextInput) -> GetTaskContextOutput:
    """AI provides multiple targeted queries for complex tasks, MCP returns relevant knowledge organized by scope hierarchy."""
    log_mcp_tool_call("get_task_context", queries=input.queries, scope=input.scope, task_size=input.task_size.value if input.task_size else None)
    try:
        task_size_value = input.task_size.value if input.task_size else None
        results = await knowledge_ops.get_task_context_knowledge(input.queries, input.scope, task_size_value)
        return GetTaskContextOutput(results=results)
    except Exception as e:
        log_error_with_context(e, {"tool": "get_task_context", "input": input.model_dump()})
        raise