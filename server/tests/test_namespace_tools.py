"""Tests for namespace MCP tools."""

import pytest
from fastmcp import Client


@pytest.mark.asyncio
async def test_list_namespaces_empty(mcp_client: Client) -> None:
    """Test listing namespaces with only global namespace."""
    async with mcp_client as client:
        result = await client.call_tool("list_namespaces", {})
        
        namespaces = result.data["namespaces"]
        assert len(namespaces) == 1
        assert "global" in namespaces


@pytest.mark.asyncio  
async def test_create_namespace(mcp_client: Client) -> None:
    """Test creating a new namespace."""
    async with mcp_client as client:
        result = await client.call_tool("create_namespace", {
            "namespace_name": "test-ns",
            "description": "Test namespace"
        })
        
        assert result.data["namespace"] == "test-ns"
        assert result.data["description"] == "Test namespace"
        assert result.data["default_scope"] == "test-ns:default"
        
        # Verify it was created
        list_result = await client.call_tool("list_namespaces", {})
        assert "test-ns" in list_result.data["namespaces"]


@pytest.mark.asyncio
async def test_list_namespaces_with_data(mcp_client: Client, conn) -> None:
    """Test listing namespaces with test data."""
    # Add test namespaces directly to DB
    await conn.execute(
        "INSERT INTO namespaces (name, description) VALUES ($1, $2)",
        "test-ns-1", "First test namespace"
    )
    await conn.execute(
        "INSERT INTO namespaces (name, description) VALUES ($1, $2)",
        "test-ns-2", "Second test namespace"
    )
    
    async with mcp_client as client:
        result = await client.call_tool("list_namespaces", {})
        
        namespaces = result.data["namespaces"]
        assert len(namespaces) == 3
        assert "global" in namespaces
        assert "test-ns-1" in namespaces
        assert "test-ns-2" in namespaces