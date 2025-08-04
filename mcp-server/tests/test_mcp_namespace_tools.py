"""Comprehensive integration tests for MCP namespace tools."""

import pytest
import asyncpg
from fastmcp import Client
from fastmcp.exceptions import ToolError
from typing import Any
import uuid
from project_kaizen.types import GLOBAL_NAMESPACE


class TestMCPNamespaceTools:
    """Test all critical namespace functionality via MCP protocol."""
    
    async def test_create_namespace_creates_default_scope(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test namespace creation automatically creates default scope."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            result = await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test project namespace"
            })
            
            assert not result.is_error
            assert result.data["name"] == namespace_name
            assert result.data["description"] == "Test project namespace"
            assert "scopes" in result.data
            assert len(result.data["scopes"]) == 1
            assert "default" in result.data["scopes"]
            
            # Verify database state
            scope = await clean_db.fetchrow("""
                SELECT s.* FROM scopes s 
                JOIN namespaces n ON s.namespace_id = n.id 
                WHERE n.name = $1 AND s.name = 'default'
            """, namespace_name)
            assert scope is not None
            assert "default scope" in scope["description"].lower()
    
    async def test_create_namespace_fails_when_duplicate_exists(self, mcp_client: Client[Any]) -> None:
        """Test duplicate namespace creation fails appropriately."""
        namespace_name = f"duplicate-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create first namespace
            result1 = await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "First creation"
            })
            assert not result1.is_error
            
            # Attempt duplicate creation
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("create_namespace", {
                    "name": namespace_name, 
                    "description": "Second creation"
                })
            
            error_msg = str(exc_info.value).lower()
            assert "duplicate" in error_msg or "already exists" in error_msg
    
    async def test_create_namespace_fails_when_invalid_name(self, mcp_client: Client[Any]) -> None:
        """Test namespace creation with invalid names fails."""
        invalid_names = [
            "UPPERCASE",  # Should be lowercase
            "spaces in name",  # No spaces allowed
            "special@chars",  # No special characters
            "",  # Empty name
            "name_with_underscores",  # Should use hyphens
            "-starts-with-hyphen",  # Cannot start with hyphen
            "ends-with-hyphen-",  # Cannot end with hyphen
        ]
        
        async with mcp_client:
            for invalid_name in invalid_names:
                with pytest.raises(ToolError) as exc_info:
                    await mcp_client.call_tool("create_namespace", {
                        "name": invalid_name,
                        "description": "Test description"
                    })
                
                error_msg = str(exc_info.value).lower()
                assert "invalid" in error_msg or "name" in error_msg
    
    async def test_get_namespaces_varies_detail_when_style_changes(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test get_namespaces returns different detail levels per style."""
        namespace_name = f"style-test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create test namespace
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Style test namespace"
            })
            
            # Test SHORT style - no scopes included
            short_result = await mcp_client.call_tool("get_namespaces", {"style": "short"})
            assert not short_result.is_error
            assert namespace_name in short_result.data["namespaces"]
            # Short style should not include scopes
            short_ns = short_result.data["namespaces"][namespace_name]
            assert "scopes" not in short_ns or short_ns["scopes"] is None
            
            # Test LONG style - includes scopes without parents
            long_result = await mcp_client.call_tool("get_namespaces", {"style": "long"})
            assert not long_result.is_error
            long_ns = long_result.data["namespaces"][namespace_name]
            assert "scopes" in long_ns
            assert "default" in long_ns["scopes"]
            # Long style should not include parent info
            default_scope = long_ns["scopes"]["default"]
            assert "parents" not in default_scope or default_scope["parents"] is None
            
            # Test DETAILS style - includes scopes with parent information
            details_result = await mcp_client.call_tool("get_namespaces", {"style": "details"})
            assert not details_result.is_error
            details_ns = details_result.data["namespaces"][namespace_name]
            assert "scopes" in details_ns
            default_scope_detailed = details_ns["scopes"]["default"]
            assert "parents" in default_scope_detailed
            assert isinstance(default_scope_detailed["parents"], list)
    
    async def test_get_namespaces_filters_by_name_when_specified(self, mcp_client: Client[Any]) -> None:
        """Test get_namespaces returns only specified namespace when name parameter provided."""
        namespace_name = f"filter-test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create test namespace
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Filter test namespace"
            })
            
            # Test filtering by specific namespace name
            filtered_result = await mcp_client.call_tool("get_namespaces", {
                "namespace": namespace_name,
                "style": "long"
            })
            
            assert not filtered_result.is_error
            namespaces = filtered_result.data["namespaces"]
            
            # Should only return the requested namespace, not global or others
            assert len(namespaces) == 1
            assert namespace_name in namespaces
            assert GLOBAL_NAMESPACE not in namespaces
            
            # Verify the returned namespace has correct data
            filtered_ns = namespaces[namespace_name]
            assert filtered_ns["description"] == "Filter test namespace"
            assert "scopes" in filtered_ns
            assert "default" in filtered_ns["scopes"]
    
    async def test_update_namespace_changes_description_only(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test updating namespace description preserves name and scopes."""
        namespace_name = f"update-desc-{uuid.uuid4().hex[:8]}"
        original_desc = "Original description"
        updated_desc = "Updated description"
        
        async with mcp_client:
            # Create namespace
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": original_desc
            })
            
            # Update description only
            result = await mcp_client.call_tool("update_namespace", {
                "name": namespace_name,
                "description": updated_desc
            })
            
            assert not result.is_error
            assert result.data["name"] == namespace_name
            assert result.data["description"] == updated_desc
            assert "scopes" in result.data
            assert "default" in result.data["scopes"]
            
            # Verify database state
            db_namespace = await clean_db.fetchrow(
                "SELECT * FROM namespaces WHERE name = $1", namespace_name
            )
            assert db_namespace is not None
            assert db_namespace["description"] == updated_desc
    
    async def test_update_namespace_renames_and_updates_references(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test namespace rename updates all scope references."""
        old_name = f"old-name-{uuid.uuid4().hex[:8]}"
        new_name = f"new-name-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace
            await mcp_client.call_tool("create_namespace", {
                "name": old_name,
                "description": "Test rename namespace"
            })
            
            # Rename namespace
            result = await mcp_client.call_tool("update_namespace", {
                "name": old_name,
                "new_name": new_name
            })
            
            assert not result.is_error
            assert result.data["name"] == new_name
            
            # Verify old name no longer exists
            old_namespace = await clean_db.fetchrow(
                "SELECT * FROM namespaces WHERE name = $1", old_name
            )
            assert old_namespace is None
            
            # Verify new name exists
            new_namespace = await clean_db.fetchrow(
                "SELECT * FROM namespaces WHERE name = $1", new_name
            )
            assert new_namespace is not None
    
    async def test_delete_namespace_removes_all_related_data(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test namespace deletion cascades to all scopes and knowledge."""
        namespace_name = f"delete-test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test delete namespace"
            })
            
            # Delete namespace
            result = await mcp_client.call_tool("delete_namespace", {
                "name": namespace_name
            })
            
            assert not result.is_error
            assert result.data["name"] == namespace_name
            assert "scopes_count" in result.data
            assert "knowledge_count" in result.data
            assert result.data["scopes_count"] >= 1  # At least default scope
            
            # Verify complete removal from database
            db_namespace = await clean_db.fetchrow(
                "SELECT * FROM namespaces WHERE name = $1", namespace_name
            )
            assert db_namespace is None
            
            # Verify scopes are also removed
            remaining_scopes = await clean_db.fetch("""
                SELECT s.* FROM scopes s 
                JOIN namespaces n ON s.namespace_id = n.id 
                WHERE n.name = $1
            """, namespace_name)
            assert len(remaining_scopes) == 0
    
    async def test_global_namespace_rejects_modifications(self, mcp_client: Client[Any]) -> None:
        """Test global namespace cannot be modified or deleted."""
        async with mcp_client:
            # Test update global namespace fails
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("update_namespace", {
                    "name": GLOBAL_NAMESPACE,
                    "description": "Modified global description"
                })
            assert "global" in str(exc_info.value).lower()
            
            # Test rename global namespace fails
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("update_namespace", {
                    "name": GLOBAL_NAMESPACE,
                    "new_name": "renamed-global"
                })
            assert "global" in str(exc_info.value).lower()
            
            # Test delete global namespace fails
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("delete_namespace", {
                    "name": GLOBAL_NAMESPACE
                })
            assert "global" in str(exc_info.value).lower()
    
    async def test_namespace_operations_fail_when_nonexistent(self, mcp_client: Client[Any]) -> None:
        """Test operations on non-existent namespaces fail appropriately."""
        nonexistent_name = f"does-not-exist-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Test update non-existent namespace
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("update_namespace", {
                    "name": nonexistent_name,
                    "description": "Some description"
                })
            assert "not found" in str(exc_info.value).lower()
            
            # Test delete non-existent namespace
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("delete_namespace", {
                    "name": nonexistent_name
                })
            assert "not found" in str(exc_info.value).lower()
