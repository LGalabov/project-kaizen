"""Test configuration for Project Kaizen MCP Server."""

import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import asyncpg
import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from testcontainers.postgres import PostgresContainer


def get_db_url(container: PostgresContainer) -> str:
    """Convert container URL to asyncpg format."""
    url: str = container.get_connection_url().replace("postgresql+psycopg2://", "postgresql://")
    return url


@pytest.fixture(scope="session")
def event_loop() -> Any:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def postgres_container() -> AsyncGenerator[PostgresContainer, None]:
    """Start PostgreSQL container and load schema once."""
    with PostgresContainer("postgres:17-alpine") as container:
        conn = await asyncpg.connect(get_db_url(container))
        db_dir = Path(__file__).parent.parent.parent / "database"
        db_test_dir = db_dir / "tests"

        await conn.execute((db_dir / "01-initial-schema.sql").read_text())
        await conn.execute((db_test_dir / "01-test-helpers.sql").read_text())
        
        await conn.close()
        yield container


@pytest.fixture
async def mcp_client(postgres_container: PostgresContainer) -> AsyncGenerator[Client[Any], None]:
    """MCP client with a clean database."""
    db_url = get_db_url(postgres_container)
    
    # Clean before test
    conn = await asyncpg.connect(db_url)
    await conn.execute("SELECT reset_test_database()")
    await conn.close()
    
    client = Client(StdioTransport(
        command="python",
        args=["-m", "project_kaizen"],
        env={"DATABASE_URL": db_url},
        cwd=str(Path(__file__).parent.parent),
    ))
    yield client
