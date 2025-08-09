"""Tests for search knowledge MCP tools."""

from typing import Any

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError


def _find_content_in_search_results(result_data: dict[str, dict[str, str]] | None, content_substring: str) -> bool:
    """Helper function to search for content substring in search results."""
    if not result_data:
        return False
    
    for scope_results in result_data.values():
        for knowledge_id, content in scope_results.items():
            if content_substring in content:
                return True
    return False


# ============================================================================
# 1. Basic Search Functionality Tests
# ============================================================================

async def test_search_basic_single_query(mcp_client: Client[Any]) -> None:
    """Searches knowledge with a single query term in the default scope.
    Verifies basic search functionality returns correct matches.
    Value: Core search operation validation."""
    async with mcp_client as client:
        # Create a namespace and add knowledge
        await client.call_tool("create_namespace", {
            "namespace_name": "search-test",
            "description": "Test namespace for search"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "search-test:default",
            "content": "This is documentation about REST API endpoints",
            "context": "api documentation rest endpoints"
        })
        
        # Search with a single query
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["api"],
            "canonical_scope_name": "search-test:default"
        })
        
        # Should find the knowledge
        assert len(result.data) > 0
        assert _find_content_in_search_results(result.data, "REST API endpoints")


async def test_search_basic_multiple_queries(mcp_client: Client[Any]) -> None:
    """Searches knowledge with multiple query terms simultaneously.
    Verifies OR logic combines results from different queries.
    Value: Multi-query search behavior."""
    async with mcp_client as client:
        # Create a namespace and add different knowledge entries
        await client.call_tool("create_namespace", {
            "namespace_name": "multi-search",
            "description": "Test namespace for multi-query search"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "multi-search:default",
            "content": "Database connection pooling configuration with postgresql read replicas and connection limits for optimal performance",
            "context": "database postgresql connection pooling configuration read replicas performance optimization"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "multi-search:default",
            "content": "Authentication system using oauth social login with jwt tokens, refresh tokens, and twofactor verification",
            "context": "authentication oauth social login jwt tokens twofactor verification security"
        })
        
        # Search with multiple queries
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["database postgresql", "authentication oauth"],
            "canonical_scope_name": "multi-search:default"
        })
        
        # Should find both pieces of knowledge
        assert len(result.data) > 0
        assert _find_content_in_search_results(result.data, "Database connection pooling")
        assert _find_content_in_search_results(result.data, "Authentication system using oauth")


async def test_search_empty_queries_validation(mcp_client: Client[Any]) -> None:
    """Validates that empty query list raises appropriate error.
    Verifies input validation prevents invalid search requests.
    Value: Error handling for malformed inputs."""
    async with mcp_client as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("search_knowledge_base", {
                "queries": [],
                "canonical_scope_name": "global:default"
            })
        
        assert "Query terms cannot be empty" in str(exc_info.value)


# ============================================================================
# 2. Scope Hierarchy Search Tests
# ============================================================================

async def test_search_scope_inheritance_chain(mcp_client: Client[Any]) -> None:
    """Searches child scope and finds knowledge from parent scopes.
    Verifies scope inheritance works correctly in search results.
    Value: Hierarchical knowledge discovery."""
    async with mcp_client as client:
        # Create namespace and scope hierarchy
        await client.call_tool("create_namespace", {
            "namespace_name": "hierarchy-test",
            "description": "Test namespace for hierarchy search"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "hierarchy-test:parent",
            "description": "Parent scope with knowledge",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "hierarchy-test:child",
            "description": "Child scope inheriting knowledge",
            "parents": ["hierarchy-test:parent"]
        })
        
        # Add knowledge to parent
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "hierarchy-test:parent",
            "content": "Parent scope contains important guidelines",
            "context": "guidelines documentation parent scope"
        })
        
        # Search from child scope should find parent's knowledge
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["guidelines"],
            "canonical_scope_name": "hierarchy-test:child"
        })
        
        # Should find the knowledge from parent scope
        assert len(result.data) > 0
        assert _find_content_in_search_results(result.data, "Parent scope contains important guidelines")


async def test_search_multiple_inheritance_levels(mcp_client: Client[Any]) -> None:
    """Searches deeply nested scope hierarchy with multiple inheritance levels.
    Verifies search traverses a complete ancestor chain.
    Value: Complex hierarchy navigation."""
    async with mcp_client as client:
        # Create a namespace and three-level hierarchy
        await client.call_tool("create_namespace", {
            "namespace_name": "deep-hierarchy",
            "description": "Test namespace for deep hierarchy search"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "deep-hierarchy:grandparent",
            "description": "Grandparent scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "deep-hierarchy:parent",
            "description": "Parent scope",
            "parents": ["deep-hierarchy:grandparent"]
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "deep-hierarchy:child",
            "description": "Child scope",
            "parents": ["deep-hierarchy:parent"]
        })
        
        # Add knowledge to grandparent
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "deep-hierarchy:grandparent",
            "content": "Ancient wisdom from the grandparent scope",
            "context": "legacy documentation grandparent scope"
        })
        
        # Search from child scope should find grandparent's knowledge
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["legacy documentation"],
            "canonical_scope_name": "deep-hierarchy:child"
        })
        
        # Should find the knowledge from grandparent scope
        assert len(result.data) > 0
        assert _find_content_in_search_results(result.data, "Ancient wisdom from the grandparent")


async def test_search_scope_isolation(mcp_client: Client[Any]) -> None:
    """Verifies knowledge in sibling scopes remains isolated without inheritance.
    Tests scope boundaries and access control.
    Value: Ensures proper knowledge encapsulation."""
    async with mcp_client as client:
        # Create namespace and sibling scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "isolation-test",
            "description": "Test namespace for scope isolation"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "isolation-test:sibling1",
            "description": "First sibling scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "isolation-test:sibling2",
            "description": "Second sibling scope",
            "parents": []
        })
        
        # Add knowledge to the first sibling only
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "isolation-test:sibling1",
            "content": "Secret information in sibling1",
            "context": "private documentation isolated scope"
        })
        
        # Search from the second sibling should not find the first sibling's knowledge
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["private"],
            "canonical_scope_name": "isolation-test:sibling2"
        })
        
        # Should not find any knowledge from sibling1 (scope isolation)
        assert not _find_content_in_search_results(result.data, "Secret information in sibling1")


# ============================================================================
# 3. Task Size Filtering Tests
# ============================================================================

async def test_search_with_task_size_filter(mcp_client: Client[Any]) -> None:
    """Filters search results by minimum task size (includes specified size and larger).
    Verifies task complexity filtering works with >= logic.
    Value: Task complexity-based knowledge retrieval with inclusive sizing."""
    async with mcp_client as client:
        # Create a namespace and add knowledge with different task sizes
        await client.call_tool("create_namespace", {
            "namespace_name": "task-size-test",
            "description": "Test namespace for task size filtering"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "task-size-test:default",
            "content": "Extra small task documentation",
            "context": "xs task guide minimal",
            "task_size": "XS"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "task-size-test:default",
            "content": "Medium task documentation",
            "context": "medium task guide standard", 
            "task_size": "M"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "task-size-test:default",
            "content": "Large task documentation",
            "context": "large task guide complex",
            "task_size": "L"
        })
        
        # Filter for Medium tasks and above (should include M, L, XL but not XS, S)
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["task guide"],
            "canonical_scope_name": "task-size-test:default",
            "task_size": "M"
        })
        
        # Should find M and L tasks, but not XS
        assert not _find_content_in_search_results(result.data, "Extra small task")
        assert _find_content_in_search_results(result.data, "Medium task")
        assert _find_content_in_search_results(result.data, "Large task")


async def test_search_without_task_size_includes_all(mcp_client: Client[Any]) -> None:
    """Search without a task size filter returns knowledge with any/no task size.
    Verifies default inclusive behavior includes all task sizes.
    Value: Ensures complete knowledge access by default."""
    async with mcp_client as client:
        # Create a namespace and add knowledge with different task sizes
        await client.call_tool("create_namespace", {
            "namespace_name": "inclusive-test",
            "description": "Test namespace for inclusive search"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "inclusive-test:default",
            "content": "Small task knowledge entry",
            "context": "small task documentation guide",
            "task_size": "S"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "inclusive-test:default",
            "content": "Large task knowledge entry",
            "context": "large task documentation guide",
            "task_size": "L"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "inclusive-test:default",
            "content": "Unclassified knowledge entry",
            "context": "general documentation guide"
        })
        
        # Search without a task size filter (should return all entries)
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["documentation guide"],
            "canonical_scope_name": "inclusive-test:default"
        })
        
        # Should find all three knowledge entries
        assert _find_content_in_search_results(result.data, "Small task knowledge")      # Task size "S" should be included
        assert _find_content_in_search_results(result.data, "Large task knowledge")     # Task size "L" should be included
        assert _find_content_in_search_results(result.data, "Unclassified knowledge")   # NULL task size should be included


async def test_search_invalid_task_size_validation(mcp_client: Client[Any]) -> None:
    """Validates invalid task size values are rejected with appropriate error.
    Tests input validation for task size parameter.
    Value: Prevents invalid filter parameters."""
    async with mcp_client as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("search_knowledge_base", {
                "queries": ["test"],
                "canonical_scope_name": "global:default",
                "task_size": "INVALID"
            })
        
        assert "Task size must be one of:" in str(exc_info.value)


# ============================================================================
# 4. Empty Results and Edge Cases
# ============================================================================

async def test_search_no_results_empty_response(mcp_client: Client[Any]) -> None:
    """Searching for non-existent terms returns no results gracefully.
    Verifies graceful handling of no matches with proper None response.
    Value: Proper empty state handling."""
    async with mcp_client as client:
        # Search for something that doesn't exist
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["nothing"],
            "canonical_scope_name": "global:default"
        })
        
        # Should return None for no results (FastMCP behavior)
        assert result.data is None
        assert not result.is_error  # Should not be an error condition


# ============================================================================
# 5. Configuration Integration Tests
# ============================================================================

async def test_search_respects_max_results_config(mcp_client: Client[Any]) -> None:
    """Verifies search respects the configured maximum results limit.
    Tests integration with configuration system.
    Value: Ensures search result limits work correctly."""
    async with mcp_client as client:
        # Create a namespace and add multiple knowledge entries
        await client.call_tool("create_namespace", {
            "namespace_name": "limit-test",
            "description": "Test namespace for result limits"
        })
        
        # Add multiple knowledge entries with the same search term
        for i in range(5):
            await client.call_tool("write_knowledge", {
                "canonical_scope_name": "limit-test:default",
                "content": f"Configuration item number {i} for testing limits",
                "context": f"configuration test item number{i}"
            })
        
        # First, verify we have more than 2 results without limit
        result_without_limit = await client.call_tool("search_knowledge_base", {
            "queries": ["configuration test"],
            "canonical_scope_name": "limit-test:default"
        })
        
        total_without_limit = sum(len(entries) for entries in result_without_limit.data.values())
        assert total_without_limit > 2, f"Expected >2 results to test limiting, got {total_without_limit}"
        
        # Set max results to 2
        await client.call_tool("update_config", {
            "key": "search.max_results",
            "value": "2"
        })
        
        # Search should return at most 2 results
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["configuration test"],
            "canonical_scope_name": "limit-test:default"
        })
        
        total_results = sum(len(entries) for entries in result.data.values())
        assert total_results <= 2
        
        # Reset config for other tests
        await client.call_tool("reset_config", {
            "key": "search.max_results"
        })


# ============================================================================
# 6. Error Handling and Edge Cases
# ============================================================================

async def test_search_nonexistent_scope(mcp_client: Client[Any]) -> None:
    """Searching in non-existent scope raises appropriate error.
    Verifies scope validation and error messaging.
    Value: Proper error handling for invalid scopes."""
    async with mcp_client as client:
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("search_knowledge_base", {
                "queries": ["test"],
                "canonical_scope_name": "nonexistent:scope"
            })
        
        assert "does not exist" in str(exc_info.value)


async def test_search_malformed_scope_name(mcp_client: Client[Any]) -> None:
    """Validates malformed scope names are rejected with clear error messages.
    Tests input validation for canonical scope format.
    Value: Prevents malformed scope references."""
    async with mcp_client as client:
        # Test malformed scope names with expected error messages
        test_cases = [
            ("no-colon-separator", "must be in format 'namespace:scope'"),
            (":missing-namespace", "Namespace name cannot be empty"),
            ("namespace:", "Scope name cannot be empty"),
            ("", "Canonical scope name cannot be empty")
        ]
        
        for malformed_name, expected_message in test_cases:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("search_knowledge_base", {
                    "queries": ["test"],
                    "canonical_scope_name": malformed_name
                })
            
            # Should get specific validation error
            assert expected_message in str(exc_info.value)
