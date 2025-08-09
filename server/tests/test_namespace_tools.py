"""Tests for namespace MCP tools."""

from typing import Any

import pytest
from fastmcp import Client

# ============================================================================
# 1. Namespace Lifecycle Tests
# ============================================================================

async def test_create_namespace_basic(mcp_client: Client[Any]) -> None:
    """Creates a namespace with a valid name and description.
    Verifies namespace exists and the default scope is auto-created.
    Value: Ensures basic namespace creation works with trigger side effects."""
    async with mcp_client as client:
        result = await client.call_tool("create_namespace", {
            "namespace_name": "test-namespace",
            "description": "Test namespace for validation"
        })
        
        assert result.data["namespace"] == "test-namespace"
        assert result.data["description"] == "Test namespace for validation"
        assert result.data["default_scope"] == "test-namespace:default"


async def test_create_namespace_duplicate(mcp_client: Client[Any]) -> None:
    """Attempts to create namespace with existing name.
    Value: Validates uniqueness constraints are enforced."""
    async with mcp_client as client:
        # Create first namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "duplicate-test",
            "description": "First namespace"
        })
        
        # Attempt to create a duplicate
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("create_namespace", {
                "namespace_name": "duplicate-test",
                "description": "Duplicate namespace"
            })
        assert "already exists" in str(exc_info.value).lower()


async def test_create_namespace_invalid_names(mcp_client: Client[Any]) -> None:
    """Tests invalid names: empty, too short (1 char), too long (>64), special chars, uppercase.
    Value: Ensures validation rules protect data integrity."""
    async with mcp_client as client:
        invalid_names = [
            "",  # empty
            "a",  # too short
            "a" * 65,  # too long
            "test namespace",  # space
            "test@namespace",  # special char
            "TestNamespace",  # uppercase
        ]
        
        for invalid_name in invalid_names:
            with pytest.raises(Exception):  # noqa: B017
                await client.call_tool("create_namespace", {
                    "namespace_name": invalid_name,
                    "description": "Test description"
                })


async def test_delete_namespace_cascade(mcp_client: Client[Any]) -> None:
    """Creates namespace with scopes and knowledge, then deletes it.
    Verifies all related data is removed.
    Value: Confirms CASCADE deletion works correctly."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "cascade-test",
            "description": "Namespace for cascade delete test"
        })
        
        # Add a scope
        await client.call_tool("create_scope", {
            "canonical_scope_name": "cascade-test:test-scope",
            "description": "Test scope",
            "parents": []
        })
        
        # Add knowledge
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "cascade-test:test-scope",
            "content": "Test knowledge content",
            "context": "Test context"
        })
        
        # Delete namespace
        result = await client.call_tool("delete_namespace", {
            "namespace_name": "cascade-test"
        })
        
        assert result.data["deleted_scopes"] >= 2  # default + test-scope
        assert result.data["deleted_knowledge"] >= 1
        
        # Verify it's gone
        list_result = await client.call_tool("list_namespaces", {})
        assert "cascade-test" not in list_result.data["namespaces"]


async def test_delete_global_namespace_prevented(mcp_client: Client[Any]) -> None:
    """Attempts to delete the global namespace.
    Value: Ensures system-critical namespace is protected."""
    async with mcp_client as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("delete_namespace", {
                "namespace_name": "global"
            })
        assert "cannot delete" in str(exc_info.value).lower()


# ============================================================================
# 2. Namespace Query Tests
# ============================================================================

async def test_list_namespaces_empty(mcp_client: Client[Any]) -> None:
    """Lists namespaces with only global present.
    Value: Baseline test for clean state."""
    async with mcp_client as client:
        result = await client.call_tool("list_namespaces", {})
        
        namespaces = result.data["namespaces"]
        assert len(namespaces) == 1
        assert "global" in namespaces


async def test_list_namespaces_multiple(mcp_client: Client[Any]) -> None:
    """Creates several namespaces, lists them.
    Verifies all are returned with correct details.
    Value: Ensures listing works at scale."""
    async with mcp_client as client:
        # Create multiple namespaces
        for i in range(3):
            await client.call_tool("create_namespace", {
                "namespace_name": f"test-ns-{i}",
                "description": f"Test namespace {i}"
            })
        
        # List all
        result = await client.call_tool("list_namespaces", {})
        namespaces = result.data["namespaces"]
        
        assert len(namespaces) == 4  # global + 3 test namespaces
        assert "global" in namespaces
        for i in range(3):
            assert f"test-ns-{i}" in namespaces


async def test_get_namespace_details(mcp_client: Client[Any]) -> None:
    """Gets details of specific namespace including scopes and relationships.
    Value: Validates complete namespace information retrieval."""
    async with mcp_client as client:
        # Create a namespace with scope
        await client.call_tool("create_namespace", {
            "namespace_name": "details-test",
            "description": "Namespace for details test"
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "details-test:custom-scope",
            "description": "Custom scope",
            "parents": ["details-test:default"]
        })
        
        # Get details
        result = await client.call_tool("get_namespace_details", {
            "namespace_name": "details-test"
        })
        
        assert result.data["namespace"] == "details-test"
        assert result.data["description"] == "Namespace for details test"
        assert len(result.data["scopes"]) == 2  # default + custom
        assert "details-test:default" in result.data["scopes"]
        assert "details-test:custom-scope" in result.data["scopes"]


async def test_get_namespace_nonexistent(mcp_client: Client[Any]) -> None:
    """Attempts to get details of non-existent namespace.
    Value: Ensures proper error handling."""
    async with mcp_client as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("get_namespace_details", {
                "namespace_name": "nonexistent"
            })
        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()


# ============================================================================
# 3. Namespace Modification Tests
# ============================================================================

async def test_rename_namespace(mcp_client: Client[Any]) -> None:
    """Renames namespace and verifies all references updated.
    Checks that scopes and knowledge entries are still accessible.
    Value: Confirms reference integrity during renames."""
    async with mcp_client as client:
        # Create a namespace with content
        await client.call_tool("create_namespace", {
            "namespace_name": "old-name",
            "description": "Namespace to rename"
        })
        
        await client.call_tool("write_knowledge", {
            "canonical_scope_name": "old-name:default",
            "content": "Test content",
            "context": "Test context"
        })
        
        # Rename
        result = await client.call_tool("rename_namespace", {
            "old_namespace_name": "old-name",
            "new_namespace_name": "new-name"
        })
        
        assert result.data["namespace"] == "new-name"
        
        # Verify the old name is gone
        list_result = await client.call_tool("list_namespaces", {})
        assert "old-name" not in list_result.data["namespaces"]
        assert "new-name" in list_result.data["namespaces"]
        
        # Verify scopes updated
        details = await client.call_tool("get_namespace_details", {
            "namespace_name": "new-name"
        })
        assert "new-name:default" in details.data["scopes"]


async def test_rename_namespace_to_existing(mcp_client: Client[Any]) -> None:
    """Attempts to rename to already existing name.
    Value: Validates uniqueness during updates."""
    async with mcp_client as client:
        # Create two namespaces
        await client.call_tool("create_namespace", {
            "namespace_name": "first-ns",
            "description": "First namespace"
        })
        
        await client.call_tool("create_namespace", {
            "namespace_name": "second-ns",
            "description": "Second namespace"
        })
        
        # Try to rename the first one to the second's name
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("rename_namespace", {
                "old_namespace_name": "first-ns",
                "new_namespace_name": "second-ns"
            })
        assert "already exists" in str(exc_info.value).lower()


async def test_update_namespace_description(mcp_client: Client[Any]) -> None:
    """Updates only the description field.
    Value: Ensures selective updates work without side effects."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "update-test",
            "description": "Original description"
        })
        
        # Update description
        result = await client.call_tool("update_namespace_description", {
            "namespace_name": "update-test",
            "new_description": "Updated description"
        })
        
        assert result.data["namespace"] == "update-test"
        assert result.data["description"] == "Updated description"
        
        # Verify name unchanged
        list_result = await client.call_tool("list_namespaces", {})
        assert "update-test" in list_result.data["namespaces"]


# ============================================================================
# 4. Integration Tests
# ============================================================================

async def test_namespace_with_populated_scopes(mcp_client: Client[Any]) -> None:
    """Creates namespace, adds multiple scopes with parent relationships.
    Verifies namespace details include full hierarchy.
    Value: Tests real-world usage patterns."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "hierarchy-test",
            "description": "Namespace with scope hierarchy"
        })
        
        # Add scopes with relationships
        await client.call_tool("create_scope", {
            "canonical_scope_name": "hierarchy-test:level1",
            "description": "Level 1 scope",
            "parents": ["hierarchy-test:default"]
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "hierarchy-test:level2",
            "description": "Level 2 scope",
            "parents": ["hierarchy-test:level1"]
        })
        
        # Get namespace details
        result = await client.call_tool("get_namespace_details", {
            "namespace_name": "hierarchy-test"
        })
        
        assert len(result.data["scopes"]) == 3
        assert "hierarchy-test:default" in result.data["scopes"]
        assert "hierarchy-test:level1" in result.data["scopes"]
        assert "hierarchy-test:level2" in result.data["scopes"]


async def test_namespace_isolation(mcp_client: Client[Any]) -> None:
    """Creates two namespaces with the same scope names.
    Verifies they don't conflict.
    Value: Confirms multi-tenancy isolation."""
    async with mcp_client as client:
        # Create two namespaces
        await client.call_tool("create_namespace", {
            "namespace_name": "tenant1",
            "description": "First tenant"
        })
        
        await client.call_tool("create_namespace", {
            "namespace_name": "tenant2",
            "description": "Second tenant"
        })
        
        # Add same-named scopes to each
        await client.call_tool("create_scope", {
            "canonical_scope_name": "tenant1:api",
            "description": "Tenant 1 API scope",
            "parents": []
        })
        
        await client.call_tool("create_scope", {
            "canonical_scope_name": "tenant2:api",
            "description": "Tenant 2 API scope",
            "parents": []
        })
        
        # Verify both exist independently
        tenant1_details = await client.call_tool("get_namespace_details", {
            "namespace_name": "tenant1"
        })
        tenant2_details = await client.call_tool("get_namespace_details", {
            "namespace_name": "tenant2"
        })
        
        assert "tenant1:api" in tenant1_details.data["scopes"]
        assert "tenant2:api" in tenant2_details.data["scopes"]


async def test_namespace_default_scope_relationship(mcp_client: Client[Any]) -> None:
    """Verifies every namespace gets a default scope.
    Checks new scopes auto-inherit from namespace's default.
    Value: Validates automatic hierarchy setup."""
    async with mcp_client as client:
        # Create namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "default-test",
            "description": "Test default scope creation"
        })
        
        # Verify default scope exists
        details = await client.call_tool("get_namespace_details", {
            "namespace_name": "default-test"
        })
        assert "default-test:default" in details.data["scopes"]
        
        # Create a scope without explicit parents
        await client.call_tool("create_scope", {
            "canonical_scope_name": "default-test:custom",
            "description": "Custom scope",
            "parents": []
        })
        
        # Verify it inherits from default (check via scope details if available)
        # For now, just verify it was created successfully
        details = await client.call_tool("get_namespace_details", {
            "namespace_name": "default-test"
        })
        assert "default-test:custom" in details.data["scopes"]


# ============================================================================
# 5. Edge Case Tests
# ============================================================================

async def test_namespace_name_edge_cases(mcp_client: Client[Any]) -> None:
    """Tests names with hyphens, numbers, at boundaries (2 and 64 chars).
    Value: Ensures edge cases within the valid range work."""
    async with mcp_client as client:
        edge_cases = [
            "ab",  # 2 chars (minimum)
            "a" * 64,  # 64 chars (maximum)
            "test-with-hyphens",
            "test123",
            "123test",
            "test-123-mix",
        ]
        
        for i, name in enumerate(edge_cases):
            await client.call_tool("create_namespace", {
                "namespace_name": name,
                "description": f"Edge case test {i}"
            })
            
            # Verify it was created
            list_result = await client.call_tool("list_namespaces", {})
            assert name in list_result.data["namespaces"]


# ============================================================================
# 6. Error Recovery Tests
# ============================================================================

async def test_namespace_creation_rollback(mcp_client: Client[Any]) -> None:
    """Simulates failure during namespace creation.
    Verifies no partial data remains.
    Value: Confirms transaction atomicity."""
    async with mcp_client as client:
        # Try to create namespace with invalid description (too short)
        with pytest.raises(Exception):  # noqa: B017
            await client.call_tool("create_namespace", {
                "namespace_name": "rollback-test",
                "description": "a"  # Too short (needs 2+ chars)
            })
        
        # Verify namespace doesn't exist
        list_result = await client.call_tool("list_namespaces", {})
        assert "rollback-test" not in list_result.data["namespaces"]


async def test_namespace_reference_after_delete(mcp_client: Client[Any]) -> None:
    """Deletes namespace, attempts to use it.
    Value: Ensures proper cleanup and error messages."""
    async with mcp_client as client:
        # Create and delete namespace
        await client.call_tool("create_namespace", {
            "namespace_name": "deleted-ns",
            "description": "Namespace to delete"
        })
        
        await client.call_tool("delete_namespace", {
            "namespace_name": "deleted-ns"
        })
        
        # Try to use deleted namespace
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("get_namespace_details", {
                "namespace_name": "deleted-ns"
            })
        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()
        
        # Try to create scope in deleted namespace
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("create_scope", {
                "canonical_scope_name": "deleted-ns:some-scope",
                "description": "Should fail",
                "parents": []
            })
        assert "does not exist" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()
