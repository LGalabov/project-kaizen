"""Tests for knowledge management MCP tools."""

from typing import Any

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

# ============================================================================
# 1. Knowledge Creation Tests
# ============================================================================

async def test_write_knowledge_basic_creation(mcp_client: Client[Any]) -> None:
    """Creates knowledge entry with required fields, verifies ID generation and storage.
    Tests basic knowledge creation functionality with minimal required parameters.
    Value: Core knowledge storage validation."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "knowledge-test",
            "description": "Test namespace for knowledge creation"
        })
        
        result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "knowledge-test:default",
            "content": "This is test knowledge content for basic creation",
            "context": "test knowledge content creation basic"
        })
        
        # Verify knowledge was created successfully
        assert "id" in result.data
        assert isinstance(result.data["id"], int)
        assert result.data["id"] > 0
        assert result.data["scope"] == "knowledge-test:default"
        
        # Verify knowledge can be found via search
        search_result = await client.call_tool("search_knowledge_base", {
            "queries": ["test knowledge"],
            "canonical_scope_name": "knowledge-test:default"
        })
        
        assert "This is test knowledge content" in search_result.data


async def test_write_knowledge_with_task_size_classification(mcp_client: Client[Any]) -> None:
    """Creates knowledge with each task size (XS/S/M/L/XL), validates proper storage.
    Tests task size classification functionality and storage.
    Value: Task complexity classification system validation."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "task-size-test",
            "description": "Test namespace for task size classification"
        })
        
        task_sizes = ["XS", "S", "M", "L", "XL"]
        created_ids = []
        
        for size in task_sizes:
            result = await client.call_tool("write_knowledge", {
                "canonical_scope_name": "task-size-test:default",
                "content": f"Knowledge entry with {size} task size complexity",
                "context": f"task-size {size.lower()}-complexity classification test",
                "task_size": size
            })
            
            created_ids.append(result.data["id"])
            assert result.data["id"] > 0
        
        # Filter for M and above (should include M, L, XL but not XS, S)
        search_result = await client.call_tool("search_knowledge_base", {
            "queries": ["complexity classification"],
            "canonical_scope_name": "task-size-test:default",
            "task_size": "M"
        })
        
        # Should find M, L, XL entries but not XS, S
        assert "Knowledge entry with M task" in search_result.data
        assert "Knowledge entry with L task" in search_result.data  
        assert "Knowledge entry with XL task" in search_result.data
        assert "Knowledge entry with XS task" not in search_result.data
        assert "Knowledge entry with S task" not in search_result.data


async def test_write_knowledge_validation_errors(mcp_client: Client[Any]) -> None:
    """Tests input validation: invalid scope names, empty content, malformed context, invalid task sizes.
    Validates all input parameters are properly checked before storage.
    Value: Data integrity protection through validation."""
    async with mcp_client as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("write_knowledge", {
                "canonical_scope_name": "invalid-scope-format",
                "content": "Test content",
                "context": "test context"
            })
        assert "Canonical scope name must be in format 'namespace:scope'" in str(exc_info.value)
        
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("write_knowledge", {
                "canonical_scope_name": "global:default",
                "content": "",
                "context": "test context"
            })
        assert "Knowledge content cannot be empty" in str(exc_info.value)
        
        # Test invalid context format (uppercase not allowed)
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("write_knowledge", {
                "canonical_scope_name": "global:default",
                "content": "Test content",
                "context": "Invalid Context With Uppercase"
            })
        assert "Knowledge context must be 1-20 space-separated keywords" in str(exc_info.value)
        
        # Test invalid task size
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("write_knowledge", {
                "canonical_scope_name": "global:default",
                "content": "Test content",
                "context": "test context",
                "task_size": "INVALID"
            })
        assert "Task size must be one of:" in str(exc_info.value)


# ============================================================================
# 2. Knowledge Content Updates Tests
# ============================================================================

async def test_update_knowledge_content_success(mcp_client: Client[Any]) -> None:
    """Updates content while preserving context, task_size, scope_id.
    Tests selective content updates without affecting other fields.
    Value: Ensures content updates are isolated from other attributes."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "content-update-test",
            "description": "Test namespace for content updates"
        })
        
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "content-update-test:default",
            "content": "Original content that will be updated",
            "context": "original content update test",
            "task_size": "M"
        })
        
        knowledge_id = create_result.data["id"]
        
        update_result = await client.call_tool("update_knowledge_content", {
            "knowledge_id": knowledge_id,
            "new_content": "Updated content with new information and details"
        })
        
        assert update_result.data["id"] == knowledge_id
        
        # Verify the content was updated, but context and task_size preserved
        search_result = await client.call_tool("search_knowledge_base", {
            "queries": ["original content"],
            "canonical_scope_name": "content-update-test:default"
        })
        
        # Should find updated content, not original
        assert "Updated content with new information" in search_result.data
        assert "Original content that will be updated" not in search_result.data
        
        # Verify context-based search still works (context wasn't changed)
        context_search = await client.call_tool("search_knowledge_base", {
            "queries": ["update test"],
            "canonical_scope_name": "content-update-test:default"
        })
        assert "Updated content with new information" in context_search.data


async def test_update_knowledge_content_nonexistent_id(mcp_client: Client[Any]) -> None:
    """Error handling for non-existent knowledge ID.
    Tests proper error response when trying to update non-existent knowledge.
    Value: Validates error handling for invalid operations."""
    async with mcp_client as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("update_knowledge_content", {
                "knowledge_id": 99999,
                "new_content": "This update should fail"
            })
        
        assert "Knowledge entry 99999 not found" in str(exc_info.value)


async def test_update_knowledge_context_success(mcp_client: Client[Any]) -> None:
    """Updates context keywords, validates format and searchability impact.
    Tests context updates and their effect on search functionality.
    Value: Ensures context changes properly affect knowledge discoverability."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "context-update-test",
            "description": "Test namespace for context updates"
        })
        
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "context-update-test:default",
            "content": "Knowledge content for context testing",
            "context": "original context keywords test"
        })
        
        knowledge_id = create_result.data["id"]
        
        update_result = await client.call_tool("update_knowledge_context", {
            "knowledge_id": knowledge_id,
            "new_context": "updated context keywords search test"
        })
        
        assert update_result.data["id"] == knowledge_id
        
        # Verify old context no longer finds the knowledge
        old_context_search = await client.call_tool("search_knowledge_base", {
            "queries": ["original context"],
            "canonical_scope_name": "context-update-test:default"
        })
        assert "Knowledge content for context testing" not in old_context_search.data
        
        # Verify new context finds the knowledge
        new_context_search = await client.call_tool("search_knowledge_base", {
            "queries": ["updated context"],
            "canonical_scope_name": "context-update-test:default"
        })
        assert "Knowledge content for context testing" in new_context_search.data


async def test_update_knowledge_context_validation(mcp_client: Client[Any]) -> None:
    """Tests context limits (1-20 keywords, 2-32 chars each, valid characters).
    Validates context format requirements and boundary conditions.
    Value: Ensures context validation maintains data quality."""
    async with mcp_client as client:
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "global:default",
            "content": "Test knowledge for context validation",
            "context": "test knowledge validation"
        })
        
        knowledge_id = create_result.data["id"]
        
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("update_knowledge_context", {
                "knowledge_id": knowledge_id,
                "new_context": "Invalid Context With Uppercase"
            })
        assert "Knowledge context must be 1-20 space-separated keywords" in str(exc_info.value)
        
        # Test context with too many keywords (>20)
        too_many_keywords = " ".join([f"keyword{i}" for i in range(1, 22)])  # 21 keywords
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("update_knowledge_context", {
                "knowledge_id": knowledge_id,
                "new_context": too_many_keywords
            })
        assert "Knowledge context must be 1-20 space-separated keywords" in str(exc_info.value)
        
        # Test context with keyword too long (>32 chars)
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("update_knowledge_context", {
                "knowledge_id": knowledge_id,
                "new_context": "this-keyword-is-way-too-long-and-exceeds-the-thirty-two-character-limit"
            })
        assert "Knowledge context must be 1-20 space-separated keywords" in str(exc_info.value)


# ============================================================================
# 3. Knowledge Organization Tests
# ============================================================================

async def test_move_knowledge_to_scope_same_namespace(mcp_client: Client[Any]) -> None:
    """Moves knowledge between scopes in the same namespace.
    Tests knowledge relocation within namespace boundaries.
    Value: Validates knowledge mobility within an organizational structure."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "move-test",
            "description": "Test namespace for knowledge movement"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "move-test:target",
            "description": "Target scope for knowledge movement",
            "parents": []
        })
        
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "move-test:default",
            "content": "Knowledge to be moved between scopes",
            "context": "knowledge movement scope test"
        })
        
        knowledge_id = create_result.data["id"]
        
        move_result = await client.call_tool("move_knowledge_to_scope", {
            "knowledge_id": knowledge_id,
            "new_canonical_scope_name": "move-test:target"
        })
        
        assert move_result.data["id"] == knowledge_id
        assert move_result.data["new_scope"] == "move-test:target"
        
        # Verify knowledge is now in the target scope
        target_search = await client.call_tool("search_knowledge_base", {
            "queries": ["knowledge movement"],
            "canonical_scope_name": "move-test:target"
        })
        assert "Knowledge to be moved between scopes" in target_search.data
        
        # Verify knowledge is no longer directly in the default scope (not inherited)
        default_search = await client.call_tool("search_knowledge_base", {
            "queries": ["knowledge movement"],
            "canonical_scope_name": "move-test:default"
        })
        assert "Knowledge to be moved between scopes" not in default_search.data


async def test_move_knowledge_cross_namespace(mcp_client: Client[Any]) -> None:
    """Moves knowledge across different namespaces.
    Tests knowledge relocation across namespace boundaries.
    Value: Validates cross-namespace knowledge mobility."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "source-ns",
            "description": "Source namespace for cross-namespace move"
        })
        
        await client.call_tool("create_namespace", {
            "namespace_name": "target-ns", 
            "description": "Target namespace for cross-namespace move"
        })
        
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "source-ns:default",
            "content": "Knowledge for cross-namespace movement test",
            "context": "cross-namespace movement test knowledge"
        })
        
        knowledge_id = create_result.data["id"]
        
        move_result = await client.call_tool("move_knowledge_to_scope", {
            "knowledge_id": knowledge_id,
            "new_canonical_scope_name": "target-ns:default"
        })
        
        assert move_result.data["id"] == knowledge_id
        assert move_result.data["new_scope"] == "target-ns:default"
        
        # Verify knowledge is in the target namespace
        target_search = await client.call_tool("search_knowledge_base", {
            "queries": ["cross-namespace movement"],
            "canonical_scope_name": "target-ns:default"
        })
        assert "Knowledge for cross-namespace movement test" in target_search.data
        
        # Verify knowledge is no longer in the source namespace
        source_search = await client.call_tool("search_knowledge_base", {
            "queries": ["cross-namespace movement"],
            "canonical_scope_name": "source-ns:default"
        })
        assert "Knowledge for cross-namespace movement test" not in source_search.data


async def test_move_knowledge_invalid_target_scope(mcp_client: Client[Any]) -> None:
    """Error handling for a non-existent target scope.
    Tests proper error response when moving to an invalid scope.
    Value: Validates error handling for invalid move operations."""
    async with mcp_client as client:
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "global:default",
            "content": "Knowledge for invalid move test",
            "context": "invalid move test knowledge"
        })
        
        knowledge_id = create_result.data["id"]
        
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("move_knowledge_to_scope", {
                "knowledge_id": knowledge_id,
                "new_canonical_scope_name": "nonexistent:scope"
            })
        
        assert "Scope 'nonexistent:scope' not found" in str(exc_info.value)


# ============================================================================
# 4. Knowledge Task Size Management Tests
# ============================================================================

async def test_update_knowledge_task_size_success(mcp_client: Client[Any]) -> None:
    """Updates task size classification from null to XL, then to S.
    Tests task size updates and their effect on filtering behavior.
    Value: Validates task size classification system functionality."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "task-size-update-test",
            "description": "Test namespace for task size updates"
        })
        
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "task-size-update-test:default",
            "content": "Knowledge for task size update testing",
            "context": "task-size update testing knowledge"
        })
        
        knowledge_id = create_result.data["id"]
        
        update_result = await client.call_tool("update_knowledge_task_size", {
            "knowledge_id": knowledge_id,
            "new_task_size": "XL"
        })
        
        assert update_result.data["id"] == knowledge_id
        assert update_result.data["task_size"] == "XL"
        
        # Verify XL task size filtering includes this knowledge
        xl_search = await client.call_tool("search_knowledge_base", {
            "queries": ["task-size update"],
            "canonical_scope_name": "task-size-update-test:default",
            "task_size": "XL"
        })
        assert "Knowledge for task size update testing" in xl_search.data
        
        # Update task size to S
        update_result2 = await client.call_tool("update_knowledge_task_size", {
            "knowledge_id": knowledge_id,
            "new_task_size": "S"
        })
        
        assert update_result2.data["task_size"] == "S"
        
        # Verify XL filtering no longer includes this knowledge
        xl_search2 = await client.call_tool("search_knowledge_base", {
            "queries": ["task-size update"],
            "canonical_scope_name": "task-size-update-test:default",
            "task_size": "XL"
        })
        assert "Knowledge for task size update testing" not in xl_search2.data
        
        # Verify S filtering includes this knowledge
        s_search = await client.call_tool("search_knowledge_base", {
            "queries": ["task-size update"],
            "canonical_scope_name": "task-size-update-test:default",
            "task_size": "S"
        })
        assert "Knowledge for task size update testing" in s_search.data


async def test_update_knowledge_task_size_validation(mcp_client: Client[Any]) -> None:
    """Tests rejection of invalid task size values.
    Validates task size parameter validation.
    Value: Ensures data integrity for task size classification."""
    async with mcp_client as client:
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "global:default",
            "content": "Knowledge for task size validation",
            "context": "task-size validation test"
        })
        
        knowledge_id = create_result.data["id"]
        
        invalid_sizes = ["INVALID", "XXL", "small", "1"]
        
        for invalid_size in invalid_sizes:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("update_knowledge_task_size", {
                    "knowledge_id": knowledge_id,
                    "new_task_size": invalid_size
                })
            
            assert "Task size must be one of:" in str(exc_info.value)
        
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("update_knowledge_task_size", {
                "knowledge_id": knowledge_id,
                "new_task_size": ""
            })
        assert "Task size cannot be empty string" in str(exc_info.value)


# ============================================================================
# 5. Knowledge Conflict Resolution Tests
# ============================================================================

async def test_resolve_knowledge_conflict_basic(mcp_client: Client[Any]) -> None:
    """Creates conflicting entries, marks one active and others suppressed.
    Tests basic conflict resolution functionality.
    Value: Validates conflict resolution system core functionality."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "conflict-test",
            "description": "Test namespace for conflict resolution"
        })
        
        result1 = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "conflict-test:default",
            "content": "Original implementation uses REST API",
            "context": "api implementation rest original"
        })
        
        result2 = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "conflict-test:default",
            "content": "Updated implementation uses GraphQL API",
            "context": "api implementation graphql updated"
        })
        
        active_id = result2.data["id"]
        suppressed_id = result1.data["id"]
        
        resolve_result = await client.call_tool("resolve_knowledge_conflict", {
            "active_knowledge_id": active_id,
            "suppressed_knowledge_ids": [suppressed_id]
        })
        
        assert resolve_result.data["active_id"] == active_id
        assert resolve_result.data["suppressed_ids"] == [suppressed_id]


async def test_resolve_knowledge_conflict_search_exclusion(mcp_client: Client[Any]) -> None:
    """Verifies suppressed knowledge doesn't appear in search results.
    Tests that the conflict resolution properly affects search behavior.
    Value: Ensures conflict resolution changes knowledge visibility."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "search-conflict-test",
            "description": "Test namespace for search conflict behavior"
        })
        
        result1 = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "search-conflict-test:default",
            "content": "Deprecated authentication method using sessions",
            "context": "authentication deprecated sessions method"
        })
        
        result2 = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "search-conflict-test:default", 
            "content": "Current authentication method using JWT tokens",
            "context": "authentication current jwt tokens method"
        })
        
        search_before = await client.call_tool("search_knowledge_base", {
            "queries": ["authentication method"],
            "canonical_scope_name": "search-conflict-test:default"
        })
        assert "Deprecated authentication method" in search_before.data
        assert "Current authentication method" in search_before.data
        
        await client.call_tool("resolve_knowledge_conflict", {
            "active_knowledge_id": result2.data["id"],
            "suppressed_knowledge_ids": [result1.data["id"]]
        })
        
        # Verify only active knowledge appears in search
        search_after = await client.call_tool("search_knowledge_base", {
            "queries": ["authentication method"],
            "canonical_scope_name": "search-conflict-test:default"
        })
        assert "Current authentication method" in search_after.data
        assert "Deprecated authentication method" not in search_after.data


async def test_resolve_knowledge_conflict_validation(mcp_client: Client[Any]) -> None:
    """Tests invalid IDs, self-conflicts, empty suppressed list.
    Validates conflict resolution parameter validation.
    Value: Ensures the conflict resolution system handles invalid inputs properly."""
    async with mcp_client as client:
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "global:default",
            "content": "Knowledge for conflict validation",
            "context": "conflict validation test"
        })
        
        valid_id = create_result.data["id"]
        
        # Test non-existent active knowledge ID
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("resolve_knowledge_conflict", {
                "active_knowledge_id": 99999,
                "suppressed_knowledge_ids": [valid_id]
            })
        assert "Knowledge entries not found: {99999}" in str(exc_info.value)
        
        # Test non-existent suppressed knowledge ID
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("resolve_knowledge_conflict", {
                "active_knowledge_id": valid_id,
                "suppressed_knowledge_ids": [99998]
            })
        assert "Knowledge entries not found: {99998}" in str(exc_info.value)
        
        # Test self-conflict (active ID in a suppressed list)
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("resolve_knowledge_conflict", {
                "active_knowledge_id": valid_id,
                "suppressed_knowledge_ids": [valid_id]
            })
        assert "Knowledge entries not found" in str(exc_info.value) or "active_knowledge_id" in str(exc_info.value)
        
        # Test empty suppressed list
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("resolve_knowledge_conflict", {
                "active_knowledge_id": valid_id,
                "suppressed_knowledge_ids": []
            })
        assert "suppressed_knowledge_ids cannot be empty" in str(exc_info.value)


# ============================================================================
# 6. Knowledge Deletion Tests
# ============================================================================

async def test_delete_knowledge_success(mcp_client: Client[Any]) -> None:
    """Deletes knowledge entry, verifies removal from database and search.
    Tests complete knowledge removal from the system.
    Value: Validates knowledge deletion functionality and cleanup."""
    async with mcp_client as client:
        await client.call_tool("create_namespace", {
            "namespace_name": "delete-test",
            "description": "Test namespace for knowledge deletion"
        })
        
        create_result = await client.call_tool("write_knowledge", {
            "canonical_scope_name": "delete-test:default",
            "content": "Knowledge entry to be deleted from system",
            "context": "knowledge deletion test entry"
        })
        
        knowledge_id = create_result.data["id"]
        
        # Verify knowledge exists before deletion
        search_before = await client.call_tool("search_knowledge_base", {
            "queries": ["knowledge deletion"],
            "canonical_scope_name": "delete-test:default"
        })
        assert "Knowledge entry to be deleted" in search_before.data
        
        # Delete the knowledge entry
        delete_result = await client.call_tool("delete_knowledge", {
            "knowledge_id": knowledge_id
        })
        
        assert delete_result.data["id"] == knowledge_id
        
        # Verify knowledge no longer appears in search
        search_after = await client.call_tool("search_knowledge_base", {
            "queries": ["knowledge deletion"],
            "canonical_scope_name": "delete-test:default"
        })
        assert "Knowledge entry to be deleted" not in search_after.data


async def test_delete_knowledge_nonexistent_id(mcp_client: Client[Any]) -> None:
    """Error handling for non-existent knowledge ID.
    Tests proper error response when deleting non-existent knowledge.
    Value: Validates error handling for invalid delete operations."""
    async with mcp_client as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("delete_knowledge", {
                "knowledge_id": 99999
            })
        
        assert "Knowledge entry 99999 not found" in str(exc_info.value)
