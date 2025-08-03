"""Integration tests for MCP namespace tools using real JSON-RPC protocol."""

import pytest
import asyncpg
from fastmcp import Client
from typing import Any
import uuid


class TestMCPNamespaceTools:
    """Test MCP namespace tools with real protocol communication and database validation."""
    
    async def test_create_namespace_success(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test successful namespace creation via MCP protocol."""
        namespace_name = f"test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace via MCP
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
            assert "description" in result.data["scopes"]["default"]
            
            namespace = await clean_db.fetchrow(
                f"SELECT * FROM namespaces WHERE name = '{namespace_name}'"
            )
            assert namespace is not None
            assert namespace["name"] == namespace_name
            assert namespace["description"] == "Test project namespace"
            
            scope = await clean_db.fetchrow(f"""
                SELECT s.* FROM scopes s 
                JOIN namespaces n ON s.namespace_id = n.id 
                WHERE n.name = '{namespace_name}' AND s.name = 'default'
            """)
            assert scope is not None, "Default scope should be created by database trigger"
    
    async def test_get_namespaces_basic(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test retrieving namespaces via MCP after creation."""
        namespace_name = f"test-get-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create a namespace first
            await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "Test get namespace"  
            })
            
            # Get all namespaces via MCP with explicit style parameter
            result = await mcp_client.call_tool("get_namespaces", {
                "style": "short"
            })
            
            assert not result.is_error
            assert "namespaces" in result.data

            namespaces_dict = result.data["namespaces"]
            namespace_names = list(namespaces_dict.keys())
            
            assert "global" in namespace_names
            assert namespace_name in namespace_names

            test_namespace = namespaces_dict[namespace_name]
            assert test_namespace["description"] == "Test get namespace"
    
    async def test_create_namespace_duplicate_error(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test creating duplicate namespace returns proper error."""
        namespace_name = f"duplicate-test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Create namespace successfully first time
            result1 = await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "First creation"
            })
            assert not result1.is_error
            assert result1.data["name"] == namespace_name
            
            # Try to create same namespace again - should raise exception due to raise_on_error=True
            from fastmcp.exceptions import ToolError
            with pytest.raises(ToolError) as exc_info:
                await mcp_client.call_tool("create_namespace", {
                    "name": namespace_name, 
                    "description": "Second creation"
                })
            
            error_msg = str(exc_info.value).lower()
            assert "already exists" in error_msg or "duplicate" in error_msg
    
    
    async def test_end_to_end_flow_validation(self, mcp_client: Client[Any], clean_db: asyncpg.Connection) -> None:
        """Test comprehensive end-to-end flow: MCP call → Database changes → MCP response."""
        namespace_name = f"e2e-test-{uuid.uuid4().hex[:8]}"
        
        async with mcp_client:
            # Step 1: Get initial namespaces count (global + any from other tests)
            initial_result = await mcp_client.call_tool("get_namespaces", {})
            assert not initial_result.is_error
            
            initial_namespaces_dict = initial_result.data["namespaces"]
            initial_count = len(initial_namespaces_dict)
            initial_namespace_names = list(initial_namespaces_dict.keys())
            assert "global" in initial_namespace_names
            
            # Step 2: Create namespace via MCP
            create_result = await mcp_client.call_tool("create_namespace", {
                "name": namespace_name,
                "description": "End-to-end test namespace"
            })
            assert not create_result.is_error
            assert create_result.data["name"] == namespace_name
            
            # Step 3: Verify database state directly
            db_namespace = await clean_db.fetchrow(
                f"SELECT * FROM namespaces WHERE name = '{namespace_name}'"
            )
            assert db_namespace is not None
            assert db_namespace["description"] == "End-to-end test namespace"
            
            # Step 4: Verify default scope was created automatically
            db_scope = await clean_db.fetchrow(f"""
                SELECT s.* FROM scopes s 
                JOIN namespaces n ON s.namespace_id = n.id 
                WHERE n.name = '{namespace_name}' AND s.name = 'default'
            """)
            assert db_scope is not None
            assert "default scope" in db_scope["description"].lower()
            
            final_result = await mcp_client.call_tool("get_namespaces", {})
            assert not final_result.is_error
            final_namespaces_dict = final_result.data["namespaces"]
            final_namespace_names = list(final_namespaces_dict.keys())
            assert len(final_namespaces_dict) == initial_count + 1
            assert namespace_name in final_namespace_names
            
            mcp_namespace = final_namespaces_dict[namespace_name]
            assert mcp_namespace["description"] == db_namespace["description"]
