"""Test configuration for Project Kaizen MCP Server.

Following best practices:
- Session-scoped container (start once)
- Function-scoped cleanup (fast isolation)
- In-memory client for fast testing (avoiding subprocess complexity)
- Clean database state for each test
"""

import os
from pathlib import Path
from typing import Any, AsyncGenerator

import asyncpg
import pytest
from fastmcp import Client
from testcontainers.postgres import PostgresContainer


# ============================================================================
# EVENT LOOP CONFIGURATION
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Any:
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
async def postgres_container() -> AsyncGenerator[PostgresContainer, None]:
    """Start PostgreSQL container once for all tests.
    
    Best practice: Session scope for containers to avoid startup overhead.
    """
    with PostgresContainer(
        image="postgres:17-alpine",
        dbname="test_db",
        username="test_user",
        password="test_pass",
    ) as container:
        # Wait for container to be ready
        container.get_connection_url()
        
        # Convert psycopg2 URL to asyncpg format
        db_url = container.get_connection_url().replace(
            "postgresql+psycopg2://", "postgresql://"
        )
        
        # Load schema once
        conn = await asyncpg.connect(db_url)
        try:
            schema_path = Path(__file__).parent.parent.parent / "database" / "01-initial-schema.sql"
            schema_sql = schema_path.read_text(encoding="utf-8")
            await conn.execute(schema_sql)
        finally:
            await conn.close()
        
        yield container


@pytest.fixture
async def db(postgres_container: PostgresContainer) -> AsyncGenerator[str, None]:
    """Provide clean database state for each test.
    
    Best practice: Function-scoped cleanup for test isolation.
    """
    # Convert psycopg2 URL to asyncpg format
    db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )
    
    # Clean database before test
    conn = await asyncpg.connect(db_url)
    try:
        # Clean all data except global namespace
        await conn.execute("""
            -- Delete all non-global namespaces (CASCADE handles everything)
            DELETE FROM namespaces WHERE name != 'global';
            
            -- Clean any extra scopes in global namespace
            DELETE FROM scopes 
            WHERE namespace_id = (SELECT id FROM namespaces WHERE name = 'global')
              AND name != 'default';
            
            -- Refresh materialized view
            REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_knowledge_search;
        """)
    finally:
        await conn.close()
    
    # Set environment for the MCP server
    os.environ["DATABASE_URL"] = db_url
    
    # Clear any existing connection pool
    from project_kaizen import database
    if database._pool is not None:
        await database._pool.close()
        database._pool = None
    
    # Re-initialize with test database
    await database.initialize()
    
    yield db_url
    
    # Cleanup after test
    if database._pool is not None:
        await database._pool.close()
        database._pool = None


@pytest.fixture
async def conn(db: str) -> AsyncGenerator[asyncpg.Connection, None]:
    """Provide a database connection for test setup.
    
    Best practice: Separate fixture for tests that need direct DB access.
    """
    connection = await asyncpg.connect(db)
    yield connection
    await connection.close()


# ============================================================================
# MCP CLIENT FIXTURES
# ============================================================================

@pytest.fixture
def mcp_client(db: str) -> Client:
    """Create MCP client for in-memory testing.
    
    For now, using in-memory client for simplicity.
    Can switch to STDIO transport once subprocess issues are resolved.
    """
    from project_kaizen.server import mcp
    return Client(mcp)