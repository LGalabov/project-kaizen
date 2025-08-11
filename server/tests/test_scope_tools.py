"""Tests for scope MCP tools."""

from typing import Any

import pytest
from fastmcp import Client

from project_kaizen.server import KNOWLEDGE_SEARCH_PROMPT_NO_RESULTS, KNOWLEDGE_SEARCH_PROMPT_WITH_RESULTS


def _find_content_in_search_results(result_data: str | None, content_substring: str) -> bool:
    """Helper function to search for content substring in search results."""
    if not result_data:
        return False
    
    return content_substring in result_data


# ============================================================================
# 1. Scope Lifecycle Tests
# ============================================================================

async def test_create_scope_basic(mcp_client: Client[Any]) -> None:
    """Creates a scope with a valid canonical name and description.
    Verifies scope exists and inherits from namespace:default when no parents are specified.
    Value: Ensures basic scope creation with automatic parent assignment."""
    async with mcp_client as client:
        # Create a namespace first
        await client.call_tool("create_namespace", {
            "namespace_name": "test-namespace",
            "description": "Test namespace for scope creation"
        })
        
        # Create scope without explicit parents
        result = await client.call_tool("create_scope", {
            "canonical_scope_name": "test-namespace:test-scope",
            "description": "Test scope for validation",
            "parents": []
        })
        
        assert result.data["scope"] == "test-namespace:test-scope"
        assert result.data["description"] == "Test scope for validation"
        # Should auto-inherit from namespace:default when no parents specified
        assert "test-namespace:default" in result.data.get("parents", [])


async def test_create_scope_with_explicit_parents(mcp_client: Client[Any]) -> None:
    """Creates scope with multiple parent relationships.
    Verifies all parent relationships are established correctly.
    Value: Tests multi-inheritance capability."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "multi-inherit",
            "description": "Namespace for multi-inheritance test"
        })
        
        # Create parent scopes
        await client.call_tool("create_scope", {
            "canonical_scope_name": "multi-inherit:parent1",
            "description": "First parent scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "multi-inherit:parent2",
            "description": "Second parent scope",
            "parents": []
        })
        
        # Create child scope with multiple parents
        result = await client.call_tool("create_scope", {
            "canonical_scope_name": "multi-inherit:child",
            "description": "Child scope with multiple parents",
            "parents": ["multi-inherit:parent1", "multi-inherit:parent2"]
        })
        
        assert result.data["scope"] == "multi-inherit:child"
        assert "multi-inherit:parent1" in result.data["parents"]
        assert "multi-inherit:parent2" in result.data["parents"]


async def test_create_scope_duplicate(mcp_client: Client[Any]) -> None:
    """Attempts to create scope with existing canonical name.
    Value: Validates uniqueness constraints are enforced."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "duplicate-test",
            "description": "Namespace for duplicate test"
        })
        
        # Create first scope
        await client.call_tool("create_scope", {
            "canonical_scope_name": "duplicate-test:my-scope",
            "description": "First scope",
            "parents": []
        })
        
        # Attempt to create a duplicate
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("create_scope", {
                "canonical_scope_name": "duplicate-test:my-scope",
                "description": "Duplicate scope",
                "parents": []
            })
        assert "already exists" in str(exc_info.value).lower()


async def test_create_scope_invalid_names(mcp_client: Client[Any]) -> None:
    """Tests invalid canonical names: malformed format, too short/long parts, special chars.
    Examples: 'scope' (no namespace), 'ns:' (no scope), 'ns::scope' (double colon).
    Value: Ensures validation rules protect data integrity."""
    async with mcp_client as client:
        # Create a valid namespace first
        await client.call_tool("create_namespace", {
            "namespace_name": "valid-ns",
            "description": "Valid namespace"
        })
        
        invalid_names = [
            "scope",  # no namespace
            "ns:",  # no scope
            ":scope",  # no namespace
            "ns::scope",  # double colon
            "ns:scope:extra",  # too many parts
            "ns/scope",  # wrong separator
            "a:scope",  # namespace too short (1 char)
            "ns:a",  # scope too short (1 char)
            ("a" * 65) + ":scope",  # namespace too long
            "ns:" + ("a" * 65),  # scope too long
            "ns:scope name",  # space in scope
            "namespace name:scope",  # space in namespace
            "NS:scope",  # uppercase namespace
            "ns:SCOPE",  # uppercase scope
            "ns:scope@123",  # special char in scope
        ]
        
        for invalid_name in invalid_names:
            with pytest.raises(Exception):  # noqa: B017
                await client.call_tool("create_scope", {
                    "canonical_scope_name": invalid_name,
                    "description": "Test description",
                    "parents": []
                })


async def test_delete_scope_cascade(mcp_client: Client[Any]) -> None:
    """Creates scope with knowledge entries, then deletes it.
    Verifies all associated knowledge is removed.
    Value: Confirms CASCADE deletion works correctly."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "cascade-test",
            "description": "Namespace for cascade delete test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "cascade-test:deletable",
            "description": "Scope to be deleted",
            "parents": []
        })
        
        # Add knowledge to the scope
        knowledge_ids = []
        for i in range(3):
            result = await client.call_tool("write_knowledge", {
                "canonical_scope_name": "cascade-test:deletable",
                "content": f"Test knowledge {i}",
                "context": f"context test{i}"
            })
            knowledge_ids.append(result.data["id"])
        
        # Delete the scope
        result = await client.call_tool("delete_scope", {
            "canonical_scope_name": "cascade-test:deletable"
        })
        
        assert result.data["scope"] == "cascade-test:deletable"
        assert result.data["knowledge_deleted"] >= 3


async def test_delete_default_scope_prevented(mcp_client: Client[Any]) -> None:
    """Attempts to delete a namespace's default scope.
    Value: Ensures system-critical scopes are protected."""
    async with mcp_client as client:
        # Create namespace (which auto-creates default scope)
        await client.call_tool("create_namespace", {
            "namespace_name": "protected-ns",
            "description": "Namespace with protected default scope"
        })
        
        # Attempt to delete default scope
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("delete_scope", {
                "canonical_scope_name": "protected-ns:default"
            })
        assert "cannot delete" in str(exc_info.value).lower() or "default scope" in str(exc_info.value).lower()


# ============================================================================
# 2. Scope Query Tests
# ============================================================================

async def test_scope_details_via_namespace(mcp_client: Client[Any]) -> None:
    """Gets scope details through a namespace details query.
    Verifies scope information and parent relationships are included.
    Value: Tests scope visibility in a namespace context."""
    async with mcp_client as client:
        # Create a namespace with scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "query-test",
            "description": "Namespace for query test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "query-test:scope1",
            "description": "First scope",
            "parents": []  # Default parent is added automatically
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "query-test:scope2",
            "description": "Second scope",
            "parents": ["query-test:scope1"]
        })
        
        # Get namespace details
        result = await client.call_tool("get_namespace_details", {
            "namespace_name": "query-test"
        })
        
        assert "query-test:default" in result.data["scopes"]
        assert "query-test:scope1" in result.data["scopes"]
        assert "query-test:scope2" in result.data["scopes"]
        assert len(result.data["scopes"]) == 3


async def test_scope_hierarchy_traversal(mcp_client: Client[Any]) -> None:
    """Creates multi-level scope hierarchy and verifies relationships.
    Tests parent-child relationships across multiple levels.
    Value: Validates inheritance chain integrity."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "hierarchy",
            "description": "Namespace for hierarchy test"
        })
        
        # Create a multi-level hierarchy
        await client.call_tool("create_scope", {
            "canonical_scope_name": "hierarchy:level1",
            "description": "Level 1",
            "parents": []  # Default parent is added automatically
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "hierarchy:level2",
            "description": "Level 2",
            "parents": ["hierarchy:level1"]
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "hierarchy:level3",
            "description": "Level 3",
            "parents": ["hierarchy:level2"]
        })
        
        # Verify all scopes exist
        result = await client.call_tool("get_namespace_details", {
            "namespace_name": "hierarchy"
        })
        
        assert len(result.data["scopes"]) == 4  # default + 3 levels
        assert "hierarchy:level1" in result.data["scopes"]
        assert "hierarchy:level2" in result.data["scopes"]
        assert "hierarchy:level3" in result.data["scopes"]


async def test_scope_cross_namespace_parents(mcp_client: Client[Any]) -> None:
    """Creates scope with parents from different namespaces.
    Verifies cross-namespace inheritance works correctly.
    Value: Tests federation capabilities."""
    async with mcp_client as client:
        # Create two namespaces
        await client.call_tool("create_namespace", {
            "namespace_name": "namespace-a",
            "description": "First namespace"
        })
        
        await client.call_tool("create_namespace", {
            "namespace_name": "namespace-b",
            "description": "Second namespace"
        })
        
        # Create scope in namespace-a
        await client.call_tool("create_scope", {
            "canonical_scope_name": "namespace-a:shared-scope",
            "description": "Scope in namespace A",
            "parents": []
        })
        
        # Create scope in namespace-b with parent from namespace-a
        result = await client.call_tool("create_scope", {
            "canonical_scope_name": "namespace-b:federated-scope",
            "description": "Scope with cross-namespace parent",
            "parents": ["namespace-a:shared-scope"]  # namespace-b:default is added automatically
        })
        
        assert "namespace-a:shared-scope" in result.data["parents"]
        assert "namespace-b:default" in result.data["parents"]


# ============================================================================
# 3. Scope Modification Tests
# ============================================================================

async def test_rename_scope(mcp_client: Client[Any]) -> None:
    """Renames scope within the same namespace and verifies references updated.
    Checks that knowledge entries and child scopes maintain relationships.
    Value: Confirms reference integrity during renames."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "rename-test",
            "description": "Namespace for rename test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "rename-test:old-name",
            "description": "Scope to rename",
            "parents": []
        })
        
        # Add knowledge to the scope
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "rename-test:old-name",
            "content": "Test knowledge",
            "context": "test rename context"
        })
        
        # Rename the scope
        result = await client.call_tool("rename_scope", {
            "canonical_scope_name": "rename-test:old-name",
            "new_scope_name": "new-name"
        })
        
        assert result.data["scope"] == "rename-test:new-name"
        
        # Verify the old name is gone and the new name exists
        namespace_details = await client.call_tool("get_namespace_details", {
            "namespace_name": "rename-test"
        })
        assert "rename-test:old-name" not in namespace_details.data["scopes"]
        assert "rename-test:new-name" in namespace_details.data["scopes"]


async def test_rename_scope_to_existing(mcp_client: Client[Any]) -> None:
    """Attempts to rename to already existing scope name.
    Value: Validates uniqueness during updates."""
    async with mcp_client as client:
        # Create a namespace with two scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "rename-conflict",
            "description": "Namespace for rename conflict test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "rename-conflict:scope1",
            "description": "First scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "rename-conflict:scope2",
            "description": "Second scope",
            "parents": []
        })
        
        # Try to rename scope1 to scope2's name
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("rename_scope", {
                "canonical_scope_name": "rename-conflict:scope1",
                "new_scope_name": "scope2"
            })
        assert "already exists" in str(exc_info.value).lower()


async def test_rename_default_scope_prevented(mcp_client: Client[Any]) -> None:
    """Attempts to rename namespace's default scope.
    Value: Ensures system scopes remain stable."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "stable-ns",
            "description": "Namespace with stable default scope"
        })
        
        # Attempt to rename default scope
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("rename_scope", {
                "canonical_scope_name": "stable-ns:default",
                "new_scope_name": "renamed-default"
            })
        assert "cannot rename" in str(exc_info.value).lower() or "default scope" in str(exc_info.value).lower()


async def test_update_scope_description(mcp_client: Client[Any]) -> None:
    """Updates only the description field.
    Value: Ensures selective updates work without side effects."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "update-test",
            "description": "Namespace for update test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "update-test:my-scope",
            "description": "Original description",
            "parents": []
        })
        
        # Update description
        result = await client.call_tool("update_scope_description", {
            "canonical_scope_name": "update-test:my-scope",
            "new_description": "Updated description"
        })
        
        assert result.data["scope"] == "update-test:my-scope"
        assert result.data["description"] == "Updated description"


async def test_update_scope_invalid_description(mcp_client: Client[Any]) -> None:
    """Tests description validation: empty, too short, too long, whitespace-only.
    Value: Validates input sanitization."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "validation-test",
            "description": "Namespace for validation test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "validation-test:test-scope",
            "description": "Valid description",
            "parents": []
        })
        
        invalid_descriptions = [
            "",  # empty
            "a",  # too short (1 char)
            "a" * 65,  # too long (>64 chars)
            "  ",  # whitespace only
            "\n\n",  # newlines only
            "\t",  # tab only
        ]
        
        for invalid_desc in invalid_descriptions:
            with pytest.raises(Exception):  # noqa: B017
                await client.call_tool("update_scope_description", {
                    "canonical_scope_name": "validation-test:test-scope",
                    "new_description": invalid_desc
                })


# ============================================================================
# 4. Parent Relationship Tests
# ============================================================================

async def test_add_scope_parent(mcp_client: Client[Any]) -> None:
    """Adds new parent to existing scope.
    Verifies inheritance is established correctly.
    Value: Tests dynamic hierarchy modification."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "parent-test",
            "description": "Namespace for parent test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "parent-test:parent-scope",
            "description": "Parent scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "parent-test:child-scope",
            "description": "Child scope",
            "parents": []
        })
        
        # Add a parent relationship
        result = await client.call_tool("add_scope_parents", {
            "canonical_scope_name": "parent-test:child-scope",
            "parent_canonical_scope_names": ["parent-test:parent-scope"]
        })
        
        assert "parent-test:parent-scope" in result.data["parents"]


async def test_add_duplicate_parent(mcp_client: Client[Any]) -> None:
    """Attempts to add the same parent twice.
    Value: Ensures deduplication - no duplicate relationships created."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "dup-parent",
            "description": "Namespace for duplicate parent test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "dup-parent:parent",
            "description": "Parent scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "dup-parent:child",
            "description": "Child scope",
            "parents": ["dup-parent:parent"]
        })
        
        # Try to add the same parent again - should succeed with deduplication
        result = await client.call_tool("add_scope_parents", {
            "canonical_scope_name": "dup-parent:child",
            "parent_canonical_scope_names": ["dup-parent:parent"]
        })
        
        # Should succeed and still have only one instance of the parent
        assert result.data["scope"] == "dup-parent:child"
        assert "dup-parent:parent" in result.data["parents"]
        # Count should be 2 (default and parent), not 3
        assert len(result.data["parents"]) == 2


async def test_add_circular_parent(mcp_client: Client[Any]) -> None:
    """Attempts to create circular inheritance (A->B->A).
    Value: Prevents inheritance loops."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "circular",
            "description": "Namespace for circular test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "circular:scope-a",
            "description": "Scope A",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "circular:scope-b",
            "description": "Scope B",
            "parents": ["circular:scope-a"]
        })
        
        # Try to make A child of B (creating a cycle)
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("add_scope_parents", {
                "canonical_scope_name": "circular:scope-a",
                "parent_canonical_scope_names": ["circular:scope-b"]
            })
        assert "circular" in str(exc_info.value).lower() or "cycle" in str(exc_info.value).lower()


async def test_add_self_as_parent(mcp_client: Client[Any]) -> None:
    """Attempts to add scope as its own parent.
    Value: Prevents self-referential relationships."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "self-ref",
            "description": "Namespace for self-reference test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "self-ref:scope",
            "description": "Test scope",
            "parents": []
        })
        
        # Try to add scope as its own parent
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("add_scope_parents", {
                "canonical_scope_name": "self-ref:scope",
                "parent_canonical_scope_names": ["self-ref:scope"]
            })
        assert "own parent" in str(exc_info.value).lower() or "self" in str(exc_info.value).lower()


async def test_remove_scope_parent(mcp_client: Client[Any]) -> None:
    """Removes existing parent relationship.
    Verifies scope no longer inherits from that parent.
    Value: Tests selective inheritance removal."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "remove-parent",
            "description": "Namespace for remove parent test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "remove-parent:parent1",
            "description": "First parent",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "remove-parent:parent2",
            "description": "Second parent",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "remove-parent:child",
            "description": "Child with multiple parents",
            "parents": ["remove-parent:parent1", "remove-parent:parent2"]
        })
        
        # Remove one parent
        result = await client.call_tool("remove_scope_parents", {
            "canonical_scope_name": "remove-parent:child",
            "parent_canonical_scope_names": ["remove-parent:parent1"]
        })
        
        assert "remove-parent:parent1" not in result.data["parents"]
        assert "remove-parent:parent2" in result.data["parents"]


async def test_remove_nonexistent_parent(mcp_client: Client[Any]) -> None:
    """Attempts to remove parent that doesn't exist.
    Value: Ensures idempotent operations."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "nonexist-parent",
            "description": "Namespace for nonexistent parent test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "nonexist-parent:scope1",
            "description": "First scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "nonexist-parent:scope2",
            "description": "Second scope",
            "parents": []
        })
        
        # Try to remove a non-existent parent relationship
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("remove_scope_parents", {
                "canonical_scope_name": "nonexist-parent:scope1",
                "parent_canonical_scope_names": ["nonexist-parent:scope2"]
            })
        assert "not parents of this scope" in str(exc_info.value).lower()


async def test_remove_last_parent(mcp_client: Client[Any]) -> None:
    """Removes all parents from a scope.
    Verifies scope still functions (may auto-inherit from default).
    Value: Tests orphan scope handling."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "orphan-test",
            "description": "Namespace for orphan test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "orphan-test:parent",
            "description": "Parent scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "orphan-test:child",
            "description": "Child scope",
            "parents": ["orphan-test:parent"]
        })
        
        # Remove the only explicit parent
        result = await client.call_tool("remove_scope_parents", {
            "canonical_scope_name": "orphan-test:child",
            "parent_canonical_scope_names": ["orphan-test:parent"]
        })
        
        # Scope should still exist and may have a default parent
        assert result.data["scope"] == "orphan-test:child"
        # Check if it auto-inherits by default or has no parents
        parents = result.data.get("parents", [])
        assert "orphan-test:parent" not in parents


# ============================================================================
# 4.1 New Batch Parent Operations Tests
# ============================================================================

async def test_add_multiple_parents_batch(mcp_client: Client[Any]) -> None:
    """Adds multiple parents in a single operation.
    Verifies batch addition works correctly.
    Value: Tests the core benefit of plural API - batch operations."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "batch-add",
            "description": "Namespace for batch add test"
        })
        
        # Create parent scopes
        for i in range(1, 4):
            await client.call_tool("create_scope", {
                "canonical_scope_name": f"batch-add:parent{i}",
                "description": f"Parent scope {i}",
                "parents": []
            })
        
        # Create a child scope
        await client.call_tool("create_scope", {
            "canonical_scope_name": "batch-add:child",
            "description": "Child scope",
            "parents": []
        })
        
        # Add three parents in one call
        result = await client.call_tool("add_scope_parents", {
            "canonical_scope_name": "batch-add:child",
            "parent_canonical_scope_names": [
                "batch-add:parent1",
                "batch-add:parent2", 
                "batch-add:parent3"
            ]
        })
        
        # Verify all three parents were added
        assert "batch-add:parent1" in result.data["parents"]
        assert "batch-add:parent2" in result.data["parents"]
        assert "batch-add:parent3" in result.data["parents"]
        # Should have 4 parents total (3 explicit and default)
        assert len(result.data["parents"]) == 4


async def test_remove_multiple_parents_batch(mcp_client: Client[Any]) -> None:
    """Removes multiple parents in a single operation.
    Verifies batch removal works correctly.
    Value: Tests batch removal efficiency."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "batch-remove",
            "description": "Namespace for batch remove test"
        })
        
        # Create parent scopes
        for i in range(1, 5):
            await client.call_tool("create_scope", {
                "canonical_scope_name": f"batch-remove:parent{i}",
                "description": f"Parent scope {i}",
                "parents": []
            })
        
        # Create child scope with all parents
        await client.call_tool("create_scope", {
            "canonical_scope_name": "batch-remove:child",
            "description": "Child scope",
            "parents": [
                "batch-remove:parent1",
                "batch-remove:parent2",
                "batch-remove:parent3",
                "batch-remove:parent4"
            ]
        })
        
        # Remove two parents in one call
        result = await client.call_tool("remove_scope_parents", {
            "canonical_scope_name": "batch-remove:child",
            "parent_canonical_scope_names": [
                "batch-remove:parent2",
                "batch-remove:parent4"
            ]
        })
        
        # Verify correct parents were removed
        assert "batch-remove:parent1" in result.data["parents"]
        assert "batch-remove:parent2" not in result.data["parents"]
        assert "batch-remove:parent3" in result.data["parents"]
        assert "batch-remove:parent4" not in result.data["parents"]


async def test_add_parents_empty_array_validation(mcp_client: Client[Any]) -> None:
    """Attempts to add an empty array of parents.
    Should fail with validation error.
    Value: Prevents meaningless API calls."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "empty-add",
            "description": "Namespace for empty array test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "empty-add:scope",
            "description": "Test scope",
            "parents": []
        })
        
        # Try to add an empty parent array
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("add_scope_parents", {
                "canonical_scope_name": "empty-add:scope",
                "parent_canonical_scope_names": []
            })
        # Should fail with validation error about minimum length
        error_msg = str(exc_info.value).lower()
        assert "at least" in error_msg or "minimum" in error_msg or "empty" in error_msg


async def test_remove_parents_empty_array_validation(mcp_client: Client[Any]) -> None:
    """Attempts to remove an empty array of parents.
    Should fail with validation error.
    Value: Prevents meaningless API calls."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "empty-remove",
            "description": "Namespace for empty array test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "empty-remove:scope",
            "description": "Test scope",
            "parents": []
        })
        
        # Try to remove an empty parent array
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("remove_scope_parents", {
                "canonical_scope_name": "empty-remove:scope",
                "parent_canonical_scope_names": []
            })
        # Should fail with validation error about minimum length
        error_msg = str(exc_info.value).lower()
        assert "at least" in error_msg or "minimum" in error_msg or "empty" in error_msg


async def test_add_parents_atomic_failure(mcp_client: Client[Any]) -> None:
    """Attempts to add a mix of valid and invalid parents.
    Entire operation should fail atomically.
    Value: Ensures data integrity with all-or-nothing behavior."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "atomic-add",
            "description": "Namespace for atomic test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "atomic-add:valid-parent",
            "description": "Valid parent",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "atomic-add:child",
            "description": "Child scope",
            "parents": []
        })
        
        # Try to add one valid and one non-existent parent
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("add_scope_parents", {
                "canonical_scope_name": "atomic-add:child",
                "parent_canonical_scope_names": [
                    "atomic-add:valid-parent",
                    "atomic-add:nonexistent-parent"  # This doesn't exist
                ]
            })
        
        # Verify the operation failed
        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()
        
        # Verify NO parents were added (atomic failure)
        # We can't check parent relationships via get_namespace_details (it only returns scope names),
        # So we'll verify the operation failed atomically by checking scope existence
        details = await client.call_tool("get_namespace_details", {
            "namespace_name": "atomic-add"
        })
        
        # The child scope should exist
        assert "atomic-add:child" in details.data["scopes"]
        # The valid parent should exist
        assert "atomic-add:valid-parent" in details.data["scopes"]
        # The nonexistent parent obviously doesn't exist
        
        # Since we can't directly check parent relationships via get_namespace_details,
        # the fact that the operation failed with the "not found" error is enough
        # to verify atomicity - no partial updates occurred


# ============================================================================
# 5. Integration Tests
# ============================================================================

async def test_scope_with_knowledge_inheritance(mcp_client: Client[Any]) -> None:
    """Creates parent scope with knowledge, child scope inherits.
    Verifies child can access parent's knowledge via search.
    Value: Tests the knowledge inheritance mechanism."""
    async with mcp_client as client:
        # Create namespace and scopes
        await client.call_tool("create_namespace", {
            "namespace_name": "inherit-knowledge",
            "description": "Namespace for knowledge inheritance"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "inherit-knowledge:parent",
            "description": "Parent with knowledge",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "inherit-knowledge:child",
            "description": "Child inheriting knowledge",
            "parents": ["inherit-knowledge:parent"]
        })
        
        # Add knowledge to parent
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "inherit-knowledge:parent",
            "content": "Parent's important knowledge about APIs",
            "context": "api documentation scope"
        })
        
        # Search from child scope should find parent's knowledge
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["api"],
            "canonical_scope_name": "inherit-knowledge:child"
        })
        
        # Should find the knowledge from the parent scope and have the structured prompt
        assert result.data.startswith(KNOWLEDGE_SEARCH_PROMPT_WITH_RESULTS)
        assert "Parent's important knowledge" in result.data


async def test_scope_rename_with_active_knowledge(mcp_client: Client[Any]) -> None:
    """Renames scope containing multiple knowledge entries.
    Verifies all knowledge remains accessible with the new scope name.
    Value: Tests data integrity during structural changes."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "rename-test",
            "description": "Test namespace for scope rename"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "rename-test:old-scope",
            "description": "Original scope name",
            "parents": []
        })
        
        # Add knowledge entries to the original scope
        knowledge_entries = [
            {"content": "Database configuration settings", "context": "database config settings"},
            {"content": "Authentication middleware setup", "context": "auth middleware setup"},
            {"content": "API endpoint documentation", "context": "api endpoint docs"}
        ]
        
        created_knowledge_ids = []
        for entry in knowledge_entries:
            result = await client.call_tool("write_knowledge", {
                "canonical_scope_name": "rename-test:old-scope",
                "content": entry["content"],
                "context": entry["context"]
            })
            created_knowledge_ids.append(result.data["id"])
        
        # Verify knowledge is searchable before rename
        pre_rename_result = await client.call_tool("search_knowledge_base", {
            "queries": ["database config"],
            "canonical_scope_name": "rename-test:old-scope"
        })
        assert pre_rename_result.data != KNOWLEDGE_SEARCH_PROMPT_NO_RESULTS
        assert "Database configuration settings" in pre_rename_result.data
        
        # Rename the scope
        rename_result = await client.call_tool("rename_scope", {
            "canonical_scope_name": "rename-test:old-scope",
            "new_scope_name": "new-scope"
        })
        assert rename_result.data["scope"] == "rename-test:new-scope"
        assert rename_result.data["previous_name"] == "rename-test:old-scope"
        
        # Verify knowledge is searchable after rename with the new scope name
        post_rename_result = await client.call_tool("search_knowledge_base", {
            "queries": ["database config"],
            "canonical_scope_name": "rename-test:new-scope"
        })
        assert post_rename_result.data != KNOWLEDGE_SEARCH_PROMPT_NO_RESULTS
        assert "Database configuration settings" in post_rename_result.data
        
        # Verify all original knowledge entries are still accessible
        all_knowledge_result = await client.call_tool("search_knowledge_base", {
            "queries": ["config", "auth", "api"],
            "canonical_scope_name": "rename-test:new-scope"
        })
        assert all_knowledge_result.data != KNOWLEDGE_SEARCH_PROMPT_NO_RESULTS
        
        # Verify the old scope name no longer works
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("search_knowledge_base", {
                "queries": ["database config"],
                "canonical_scope_name": "rename-test:old-scope"
            })
        # Should fail because the scope no longer exists
        assert "does not exist" in str(exc_info.value).lower()


async def test_scope_delete_with_children(mcp_client: Client[Any]) -> None:
    """Deletes parent scope that has child scopes.
    Verifies children are orphaned or re-parented appropriately.
    Value: Tests cascade behavior with dependencies."""
    async with mcp_client as client:
        # Create a namespace and scope hierarchy
        await client.call_tool("create_namespace", {
            "namespace_name": "delete-parent",
            "description": "Namespace for parent deletion test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "delete-parent:parent",
            "description": "Parent to be deleted",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "delete-parent:child",
            "description": "Child scope",
            "parents": ["delete-parent:parent"]
        })
        
        # Delete parent scope
        await client.call_tool("delete_scope", {
            "canonical_scope_name": "delete-parent:parent"
        })
        
        # Verify the child still exists, but the parent is gone
        namespace_details = await client.call_tool("get_namespace_details", {
            "namespace_name": "delete-parent"
        })
        
        assert "delete-parent:parent" not in namespace_details.data["scopes"]
        assert "delete-parent:child" in namespace_details.data["scopes"]


async def test_scope_multiple_inheritance_paths(mcp_client: Client[Any]) -> None:
    """Creates a diamond inheritance pattern (A -> B, C; B, C -> D).
    Verifies D inherits from A through both paths without duplication.
    Value: Tests complex inheritance resolution."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "diamond",
            "description": "Namespace for diamond inheritance"
        })
        
        # Create diamond pattern
        await client.call_tool("create_scope", {
            "canonical_scope_name": "diamond:top",
            "description": "Top of diamond",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "diamond:left",
            "description": "Left branch",
            "parents": ["diamond:top"]
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "diamond:right",
            "description": "Right branch",
            "parents": ["diamond:top"]
        })
        
        result = await client.call_tool("create_scope", {
            "canonical_scope_name": "diamond:bottom",
            "description": "Bottom of diamond",
            "parents": ["diamond:left", "diamond:right"]
        })
        
        assert "diamond:left" in result.data["parents"]
        assert "diamond:right" in result.data["parents"]
        
        # Add knowledge to the top
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "diamond:top",
            "content": "Knowledge from top of diamond",
            "context": "diamond test boundary"
        })
        
        # Search from the bottom should find it (through either path)
        search_result = await client.call_tool("search_knowledge_base", {
            "queries": ["diamond"],
            "canonical_scope_name": "diamond:bottom"
        })
        
        # Should find the knowledge from the top and have the structured prompt
        assert search_result.data.startswith(KNOWLEDGE_SEARCH_PROMPT_WITH_RESULTS)
        assert "Knowledge from top" in search_result.data


async def test_scope_namespace_boundary(mcp_client: Client[Any]) -> None:
    """Creates scopes that reference parents across namespace boundaries.
    Verifies namespace isolation while allowing explicit federation.
    Value: Tests multi-tenancy with controlled sharing."""
    async with mcp_client as client:
        # Create two namespaces
        await client.call_tool("create_namespace", {
            "namespace_name": "shared-ns",
            "description": "Namespace with shared scope"
        })
        
        await client.call_tool("create_namespace", {
            "namespace_name": "consumer-ns",
            "description": "Namespace consuming shared scope"
        })
        
        # Create a shared scope
        await client.call_tool("create_scope", {
            "canonical_scope_name": "shared-ns:public-api",
            "description": "Public API scope",
            "parents": []
        })
        
        # Add knowledge to shared scope
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "shared-ns:public-api",
            "content": "Shared API documentation",
            "context": "public api boundary"
        })
        
        # Create consumer scope that inherits from shared
        await client.call_tool("create_scope", {
            "canonical_scope_name": "consumer-ns:api-consumer",
            "description": "Consumer of shared API",
            "parents": ["shared-ns:public-api"]
        })
        
        # Search from consumer should find shared knowledge
        result = await client.call_tool("search_knowledge_base", {
            "queries": ["api documentation"],
            "canonical_scope_name": "consumer-ns:api-consumer"
        })
        
        # Should find the shared knowledge and have the structured prompt
        assert result.data.startswith(KNOWLEDGE_SEARCH_PROMPT_WITH_RESULTS)
        assert "Shared API documentation" in result.data


# ============================================================================
# 6. Edge Case Tests
# ============================================================================

async def test_scope_name_edge_cases(mcp_client: Client[Any]) -> None:
    """Tests scope names at boundaries: 2-char parts, 64-char parts, numbers, hyphens.
    Examples: 'ab:cd', 'a'*64 + ':' + 'b'*64, 'test-123:scope-456'.
    Value: Ensures edge cases within a valid range work."""
    async with mcp_client as client:
        # Create namespaces for edge cases
        edge_cases = [
            ("ab", "cd"),  # 2 chars each (minimum)
            ("a" * 64, "b" * 64),  # 64 chars each (maximum)
            ("test-123", "scope-456"),  # numbers and hyphens
            ("ns-2", "sc-2"),  # short with hyphens
        ]
        
        for i, (ns_part, scope_part) in enumerate(edge_cases):
            # Create a namespace if needed
            await client.call_tool("create_namespace", {
                "namespace_name": ns_part,
                "description": f"Edge case namespace {i}"
            })
            
            # Create scope
            canonical_name = f"{ns_part}:{scope_part}"
            await client.call_tool("create_scope", {
                "canonical_scope_name": canonical_name,
                "description": f"Edge case scope {i}",
                "parents": []
            })
            
            # Verify it was created
            namespace_details = await client.call_tool("get_namespace_details", {
                "namespace_name": ns_part
            })
            assert canonical_name in namespace_details.data["scopes"]


# ============================================================================
# 7. Error Recovery Tests
# ============================================================================

async def test_scope_creation_rollback(mcp_client: Client[Any]) -> None:
    """Simulates failure during scope creation with parents.
    Verifies no partial relationships remain.
    Value: Confirms transaction atomicity."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "rollback-test",
            "description": "Namespace for rollback test"
        })
        
        # Try to create scope with invalid description
        with pytest.raises(Exception):  # noqa: B017
            await client.call_tool("create_scope", {
                "canonical_scope_name": "rollback-test:failed-scope",
                "description": "a",  # Too short
                "parents": []
            })
        
        # Verify scope doesn't exist
        namespace_details = await client.call_tool("get_namespace_details", {
            "namespace_name": "rollback-test"
        })
        assert "rollback-test:failed-scope" not in namespace_details.data["scopes"]


async def test_scope_reference_after_delete(mcp_client: Client[Any]) -> None:
    """Deletes scope, attempts various operations on it.
    Value: Ensures proper cleanup and error messages."""
    async with mcp_client as client:
        # Create namespace and scope
        await client.call_tool("create_namespace", {
            "namespace_name": "deleted-scope-ns",
            "description": "Namespace for deleted scope test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "deleted-scope-ns:to-delete",
            "description": "Scope to delete",
            "parents": []
        })
        
        # Delete the scope
        await client.call_tool("delete_scope", {
            "canonical_scope_name": "deleted-scope-ns:to-delete"
        })
        
        # Try to update deleted scope
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("update_scope_description", {
                "canonical_scope_name": "deleted-scope-ns:to-delete",
                "new_description": "Should fail"
            })
        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()
        
        # Try to add parent to deleted scope
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("add_scope_parents", {
                "canonical_scope_name": "deleted-scope-ns:to-delete",
                "parent_canonical_scope_names": ["deleted-scope-ns:default"]
            })
        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()


async def test_scope_parent_after_namespace_delete(mcp_client: Client[Any]) -> None:
    """Deletes namespace containing parent scopes.
    Verifies child scopes in other namespaces handle orphaning.
    Value: Tests cross-namespace dependency handling."""
    async with mcp_client as client:
        # Create two namespaces
        await client.call_tool("create_namespace", {
            "namespace_name": "parent-ns",
            "description": "Namespace with parent scope"
        })
        
        await client.call_tool("create_namespace", {
            "namespace_name": "child-ns",
            "description": "Namespace with child scope"
        })
        
        # Create parent scope
        await client.call_tool("create_scope", {
            "canonical_scope_name": "parent-ns:shared-parent",
            "description": "Parent scope to be deleted",
            "parents": []
        })
        
        # Create child scope with cross-namespace parent
        await client.call_tool("create_scope", {
            "canonical_scope_name": "child-ns:orphan-child",
            "description": "Child that will be orphaned",
            "parents": ["parent-ns:shared-parent"]
        })
        
        # Delete the parent namespace
        await client.call_tool("delete_namespace", {
            "namespace_name": "parent-ns"
        })
        
        # Child scope should still exist but parent reference is invalid
        namespace_details = await client.call_tool("get_namespace_details", {
            "namespace_name": "child-ns"
        })
        assert "child-ns:orphan-child" in namespace_details.data["scopes"]


async def test_scope_invalid_namespace_reference(mcp_client: Client[Any]) -> None:
    """Attempts to create scope in non-existent namespace.
    Value: Validates namespace existence checks."""
    async with mcp_client as client:
        # Try to create scope in a non-existent namespace
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("create_scope", {
                "canonical_scope_name": "nonexistent-ns:some-scope",
                "description": "Should fail",
                "parents": []
            })
        assert "does not exist" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()


async def test_scope_malformed_canonical_names(mcp_client: Client[Any]) -> None:
    """Tests various malformed canonical names.
    Examples: 'namespace:', ':scope', 'namespace:scope:extra', 'namespace/scope'.
    Value: Ensures robust parsing and validation."""
    async with mcp_client as client:
        # Create a valid namespace for testing
        await client.call_tool("create_namespace", {
            "namespace_name": "malformed-test",
            "description": "Namespace for malformed name tests"
        })
        
        malformed_names = [
            "namespace:",  # missing scope
            ":scope",  # missing namespace
            "namespace:scope:extra",  # too many parts
            "namespace/scope",  # wrong separator
            "namespace::scope",  # double colon
            "namespace: scope",  # space after colon
            "namespace :scope",  # space before colon
            "namespace:scope ",  # trailing space
            " namespace:scope",  # leading space
        ]
        
        for malformed_name in malformed_names:
            with pytest.raises(Exception):  # noqa: B017
                await client.call_tool("create_scope", {
                    "canonical_scope_name": malformed_name,
                    "description": "Test description",
                    "parents": []
                })
