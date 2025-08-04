"""Test configuration and fixtures for Project Kaizen MCP server integration tests."""

import asyncio
import asyncpg
import pytest
from pathlib import Path
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from typing import AsyncGenerator, Any
from project_kaizen.types import GLOBAL_NAMESPACE

# Path to the schema file (relative to mcp-server directory)
SCHEMA_PATH = Path(__file__).parent.parent.parent / "database" / "01-initial-schema.sql"


@pytest.fixture(scope="session")
def event_loop() -> Any:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def postgres_container() -> AsyncGenerator[PostgresContainer, None]:
    """Start PostgreSQL container with schema-only loading (no sample data)."""
    with PostgresContainer(
        image="postgres:17-alpine",
        dbname="kz_knowledge",
        username="kz_user",
        password="kz_password",
    ) as container:
        # Wait for container to be ready
        container.get_connection_url()

        # Connect and load schema only
        # Convert psycopg2 URL to asyncpg format
        db_url = container.get_connection_url().replace(
            "postgresql+psycopg2://", "postgresql://"
        )
        conn = await asyncpg.connect(db_url)

        # Read and execute the schema SQL
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        await conn.execute(schema_sql)
        await conn.close()

        yield container


@pytest.fixture
async def clean_db(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[asyncpg.Connection, None]:
    """Provide a clean database connection for each test with schema loaded but no data."""
    # Convert psycopg2 URL to asyncpg format
    db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )
    conn = await asyncpg.connect(db_url)

    # Clean all tables but keep schema structure
    await conn.execute("""
        TRUNCATE TABLE knowledge_conflicts, knowledge, scope_hierarchy, scope_parents, scopes, namespaces RESTART IDENTITY CASCADE;
    """)

    # Insert global namespace (triggers will create default scope automatically)
    await conn.execute("""
        INSERT INTO namespaces (name, description) 
        VALUES ($1, 'Universal knowledge accessible everywhere')
        ON CONFLICT (name) DO NOTHING;
    """, GLOBAL_NAMESPACE)

    yield conn
    await conn.close()


@pytest.fixture
async def mcp_client(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[Client[Any], None]:
    """Create FastMCP client connected to the MCP server with test database."""
    # Set environment variable for the test database URL
    db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )

    # Create STDIO transport with test database URL
    transport = StdioTransport(
        command="python",
        args=["-m", "project_kaizen"],
        env={"POSTGRES_URL": db_url},
        cwd=str(Path(__file__).parent.parent),  # mcp-server directory
    )

    client = Client(transport)

    try:
        yield client
    finally:
        # Cleanup handled by Client context manager
        pass


@pytest.fixture
def test_namespace_name() -> str:
    """Provide a consistent test namespace name."""
    return "test-integration"


@pytest.fixture
def test_scope_name(test_namespace_name: str) -> str:
    """Provide a consistent test scope name."""
    return f"{test_namespace_name}:test-scope"

