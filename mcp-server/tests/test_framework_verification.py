"""Test to verify the integration test framework is working correctly."""

import pytest
import asyncpg
from fastmcp import Client
from typing import Any
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]


class TestFrameworkVerification:
    """Verify that our test framework setup is working correctly."""

    async def test_postgres_container_starts(self, postgres_container: PostgresContainer) -> None:
        """Test that PostgreSQL container starts and is accessible."""
        db_url = postgres_container.get_connection_url().replace(
            "postgresql+psycopg2://", "postgresql://"
        )
        conn = await asyncpg.connect(db_url)
        result = await conn.fetchrow("SELECT version()")
        assert result is not None
        assert "PostgreSQL" in result["version"]
        await conn.close()

    async def test_schema_loaded(self, clean_db: asyncpg.Connection) -> None:
        """Test that the database schema is properly loaded."""
        # Check that key tables exist
        tables = await clean_db.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)

        table_names = {row["table_name"] for row in tables}
        expected_tables = {
            "namespaces",
            "scopes",
            "scope_parents",
            "scope_hierarchy",
            "knowledge",
            "knowledge_conflicts",
            "config",
        }

        assert expected_tables.issubset(table_names), (
            f"Missing tables: {expected_tables - table_names}"
        )

    async def test_global_namespace_exists(self, clean_db: asyncpg.Connection) -> None:
        """Test that global namespace and default scope are created."""
        # Check global namespace exists
        namespace = await clean_db.fetchrow(
            "SELECT * FROM namespaces WHERE name = 'global'"
        )
        assert namespace is not None
        assert namespace["description"] == "Universal knowledge accessible everywhere"

        # Check default scope exists
        scope = await clean_db.fetchrow("""
            SELECT s.* FROM scopes s 
            JOIN namespaces n ON s.namespace_id = n.id 
            WHERE n.name = 'global' AND s.name = 'default'
        """)
        assert scope is not None
        assert "default scope" in scope["description"].lower()

    async def test_clean_db_isolation(self, clean_db: asyncpg.Connection) -> None:
        """Test that each test gets a clean database."""
        # Insert test data
        result = await clean_db.fetchrow("""
            INSERT INTO namespaces (name, description) 
            VALUES ('test-isolation', 'Test isolation namespace')
            RETURNING id
        """)
        assert result is not None

        # Verify it exists
        namespace = await clean_db.fetchrow(
            "SELECT * FROM namespaces WHERE name = 'test-isolation'"
        )
        assert namespace is not None

    async def test_second_clean_db_isolation(self, clean_db: asyncpg.Connection) -> None:
        """Test that previous test data is cleaned up."""
        # This test should NOT see the data from the previous test
        namespace = await clean_db.fetchrow(
            "SELECT * FROM namespaces WHERE name = 'test-isolation'"
        )
        assert namespace is None  # Should be cleaned up

    @pytest.mark.skip(reason="MCP client test - requires MCP server implementation")
    async def test_mcp_client_connection(self, mcp_client: Client[Any]) -> None:
        """Test that MCP client can connect to server (placeholder for now)."""
        # This test is skipped until we have the MCP server implementation
        # Once implemented, this should test:
        # tools = await mcp_client.list_tools()
        # assert len(tools) == 12
        pass

    def test_fixtures_available(self, test_namespace_name: str, test_scope_name: str) -> None:
        """Test that helper fixtures provide expected values."""
        assert test_namespace_name == "test-integration"
        assert test_scope_name == "test-integration:test-scope"
