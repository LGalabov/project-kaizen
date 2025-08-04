"""Comprehensive integration tests for MCP scope tools."""

import pytest
import asyncpg
from fastmcp import Client
from fastmcp.exceptions import ToolError
from typing import Any
import uuid
from project_kaizen.types import DEFAULT_SCOPE_NAME


class TestMCPScopeTools:
    """Test all critical scope functionality via MCP protocol."""
    
    async def test_create_scope_adds_default_parent_automatically(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test scope creation automatically adds default parent even when other parents specified."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace first
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test namespace for scope creation"
            })
            
            # Create first scope to be a parent
            await mcp_client.call_tool("create_scope", {
                "scope": f"{namespace_name}:parent-scope",
                "description": "Parent scope"
            })
            
            # Create scope with explicit parent - should auto-add default parent
            result = await mcp_client.call_tool("create_scope", {
                "scope": f"{namespace_name}:child-scope",
                "description": "Child scope with explicit parent",
                "parents": [f"{namespace_name}:parent-scope"]
            })
            
            assert not result.is_error
            assert result.data.scope == f"{namespace_name}:child-scope"
            assert result.data.description == "Child scope with explicit parent"
            
            # Verify both explicit and auto-added default parents are present
            parents = result.data.parents
            assert f"{namespace_name}:parent-scope" in parents
            assert f"{namespace_name}:{DEFAULT_SCOPE_NAME}" in parents
            assert len(parents) == 2
    
    async def test_update_scope_preserves_default_parent_always(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test scope update preserves default parent even when not explicitly specified in new parents."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace and scopes
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test namespace"
            })
            
            await mcp_client.call_tool("create_scope", {
                "scope": f"{namespace_name}:new-parent",
                "description": "New parent scope"
            })
            
            await mcp_client.call_tool("create_scope", {
                "scope": f"{namespace_name}:test-scope",
                "description": "Test scope"
            })
            
            # Update scope parents without including default - should auto-preserve default
            result = await mcp_client.call_tool("update_scope", {
                "scope": f"{namespace_name}:test-scope",
                "parents": [f"{namespace_name}:new-parent"]
            })
            
            assert not result.is_error
            parents = result.data.parents
            assert f"{namespace_name}:new-parent" in parents
            assert f"{namespace_name}:{DEFAULT_SCOPE_NAME}" in parents
            assert len(parents) == 2
    
    async def test_delete_scope_removes_knowledge_and_returns_count(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test scope deletion cascades to knowledge and returns correct count."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        scope_name = "test-scope"
        full_scope = f"{namespace_name}:{scope_name}"
        
        async with mcp_client:
            # Create namespace and scope
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test namespace"
            })
            
            await mcp_client.call_tool("create_scope", {
                "scope": full_scope,
                "description": "Test scope"
            })
            
            # Add knowledge entries to the scope
            await mcp_client.call_tool("write_knowledge", {
                "scope": full_scope,
                "content": "First knowledge entry",
                "context": "test context"
            })
            
            await mcp_client.call_tool("write_knowledge", {
                "scope": full_scope,
                "content": "Second knowledge entry", 
                "context": "test context"
            })
            
            # Delete scope
            result = await mcp_client.call_tool("delete_scope", {
                "scope": full_scope
            })
            
            assert not result.is_error
            assert result.data.scope == full_scope
            assert result.data.knowledge_deleted == 2
            
            # Verify scope is removed from database
            scope_check = await clean_db.fetchrow("""
                SELECT s.* FROM scopes s 
                JOIN namespaces n ON s.namespace_id = n.id 
                WHERE n.name = $1 AND s.name = $2
            """, namespace_name, scope_name)
            assert scope_check is None
    
    async def test_create_scope_fails_when_parent_not_found(self, mcp_client: Client[Any]) -> None:
        """Test scope creation fails when specified parent scope doesn't exist."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test namespace"
            })
            
            # Try to create scope with non-existent parent
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("create_scope", {
                    "scope": f"{namespace_name}:test-scope",
                    "description": "Test scope",
                    "parents": [f"{namespace_name}:nonexistent-parent"]
                })
            
            error_msg = str(exc_info.value).lower()
            assert "parent" in error_msg and ("not found" in error_msg or "does not exist" in error_msg)
    
    async def test_update_scope_fails_when_circular_reference_detected(self, mcp_client: Client[Any]) -> None:
        """Test scope update prevents circular parent references."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test namespace"
            })
            
            # Create parent-child chain: A -> B
            await mcp_client.call_tool("create_scope", {
                "scope": f"{namespace_name}:scope-a",
                "description": "Scope A"
            })
            
            await mcp_client.call_tool("create_scope", {
                "scope": f"{namespace_name}:scope-b",
                "description": "Scope B",
                "parents": [f"{namespace_name}:scope-a"]
            })
            
            # Try to create circular reference: B -> A (making A -> B -> A)
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("update_scope", {
                    "scope": f"{namespace_name}:scope-a",
                    "parents": [f"{namespace_name}:scope-b"]
                })
            
            error_msg = str(exc_info.value).lower()
            assert "circular" in error_msg or "cycle" in error_msg
    
    async def test_create_scope_supports_multiple_parents_across_namespaces(self, mcp_client: Client[Any]) -> None:
        """Test scope can have parents from different namespaces."""
        ns1 = f"ns1-{uuid.uuid4().hex[:8]}"
        ns2 = f"ns2-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create two namespaces
            await mcp_client.call_tool("create_namespace", {
                "name": ns1,
                "description": "First namespace"
            })
            
            await mcp_client.call_tool("create_namespace", {
                "name": ns2,
                "description": "Second namespace"
            })
            
            # Create parent scope in second namespace
            await mcp_client.call_tool("create_scope", {
                "scope": f"{ns2}:shared-parent",
                "description": "Shared parent scope"
            })
            
            # Create scope in first namespace with parent from second namespace
            result = await mcp_client.call_tool("create_scope", {
                "scope": f"{ns1}:cross-ns-child",
                "description": "Child scope with cross-namespace parent",
                "parents": [f"{ns2}:shared-parent"]
            })
            
            assert not result.is_error
            parents = result.data.parents
            assert f"{ns2}:shared-parent" in parents
            assert f"{ns1}:{DEFAULT_SCOPE_NAME}" in parents
            assert len(parents) == 2
    
    async def test_create_scope_fails_when_namespace_not_found(self, mcp_client: Client[Any]) -> None:
        """Test scope creation fails when target namespace doesn't exist."""
        nonexistent_namespace = f"nonexistent-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("create_scope", {
                    "scope": f"{nonexistent_namespace}:test-scope",
                    "description": "Test scope"
                })
            
            error_msg = str(exc_info.value).lower()
            assert "namespace" in error_msg and ("not found" in error_msg or "does not exist" in error_msg)
    
    async def test_scope_names_unique_within_namespace_but_allow_cross_namespace_duplicates(self, mcp_client: Client[Any]) -> None:
        """Test scope names are unique within namespace but can duplicate across namespaces."""
        ns1 = f"ns1-{uuid.uuid4().hex[:8]}"
        ns2 = f"ns2-{uuid.uuid4().hex[:8]}"
        scope_name = "common-scope"
        
        async with mcp_client:
            # Create two namespaces
            await mcp_client.call_tool("create_namespace", {
                "name": ns1,
                "description": "First namespace"
            })
            
            await mcp_client.call_tool("create_namespace", {
                "name": ns2,
                "description": "Second namespace"
            })
            
            # Create scope with same name in both namespaces - should succeed
            result1 = await mcp_client.call_tool("create_scope", {
                "scope": f"{ns1}:{scope_name}",
                "description": "Scope in first namespace"
            })
            assert not result1.is_error
            
            result2 = await mcp_client.call_tool("create_scope", {
                "scope": f"{ns2}:{scope_name}",
                "description": "Scope in second namespace"
            })
            assert not result2.is_error
            
            # Try to create duplicate in same namespace - should fail
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("create_scope", {
                    "scope": f"{ns1}:{scope_name}",
                    "description": "Duplicate scope in first namespace"
                })
            
            error_msg = str(exc_info.value).lower()
            assert "duplicate" in error_msg or "already exists" in error_msg
    
    async def test_delete_scope_fails_when_attempting_default_scope_deletion(self, mcp_client: Client[Any]) -> None:
        """Test deletion of default scope fails at model validation level."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace (automatically creates default scope)
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test namespace"
            })
            
            # Try to delete default scope - should fail during validation
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("delete_scope", {
                    "scope": f"{namespace_name}:{DEFAULT_SCOPE_NAME}"
                })
            
            error_msg = str(exc_info.value).lower()
            assert "default" in error_msg
    
    async def test_update_scope_fails_when_renaming_default_scope(self, mcp_client: Client[Any]) -> None:
        """Test renaming default scope fails."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test namespace"
            })
            
            # Try to rename default scope - should fail
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("update_scope", {
                    "scope": f"{namespace_name}:{DEFAULT_SCOPE_NAME}",
                    "new_scope": f"{namespace_name}:renamed-default"
                })
            
            error_msg = str(exc_info.value).lower()
            assert "default" in error_msg
    
    async def test_scope_operations_fail_with_invalid_format(self, mcp_client: Client[Any]) -> None:
        """Test scope operations fail with various invalid scope formats."""
        invalid_scopes = [
            "no-colon-scope",  # Missing colon
            ":empty-namespace",  # Empty namespace
            "namespace:",  # Empty scope name
            "namespace:scope:extra",  # Too many colons
            "",  # Empty string
            "namespace:scope with spaces",  # Spaces in scope name
            "namespace:scope@special",  # Special characters
        ]
        
        async with mcp_client:
            for invalid_scope in invalid_scopes:
                # Test create_scope with invalid format
                with pytest.raises(ToolError) as exc_info:
                    await mcp_client.call_tool("create_scope", {
                        "scope": invalid_scope,
                        "description": "Test description"
                    })
                
                error_msg = str(exc_info.value).lower()
                assert "format" in error_msg or "invalid" in error_msg or "scope" in error_msg or "short" in error_msg or "validation" in error_msg
    
    async def test_scope_operations_fail_when_scope_not_found(self, mcp_client: Client[Any]) -> None:
        """Test update and delete operations fail appropriately when scope doesn't exist."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        nonexistent_scope = f"{namespace_name}:nonexistent"
        
        async with mcp_client:
            # Create namespace to make the scope format valid
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test namespace"
            })
            
            # Test update non-existent scope
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("update_scope", {
                    "scope": nonexistent_scope,
                    "description": "Updated description"
                })
            
            error_msg = str(exc_info.value).lower()
            assert "not found" in error_msg
            
            # Test delete non-existent scope
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("delete_scope", {
                    "scope": nonexistent_scope
                })
            
            error_msg = str(exc_info.value).lower()
            assert "not found" in error_msg