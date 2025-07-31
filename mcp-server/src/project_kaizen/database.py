"""Database connection management for Project Kaizen MCP server."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
import structlog
from asyncpg import Pool
from asyncpg.pool import PoolConnectionProxy

from .config import settings
from .exceptions import DatabaseError

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """AsyncPG connection pool manager for MCP server operations."""

    def __init__(self) -> None:
        self._pool: Pool[asyncpg.Record] | None = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize database connection pool."""
        if self._pool is not None:
            return

        async with self._lock:
            if self._pool is not None:
                return

            try:
                logger.info("Initializing database connection pool", dsn_host=settings.database.host)
                self._pool = await asyncpg.create_pool(
                    dsn=settings.database.dsn,
                    min_size=settings.database.min_connections,
                    max_size=settings.database.max_connections,
                    command_timeout=30,
                )
                logger.info(
                    "Database pool initialized successfully",
                    min_connections=settings.database.min_connections,
                    max_connections=settings.database.max_connections,
                )
            except Exception as e:
                logger.error("Failed to initialize database pool", error=str(e))
                raise DatabaseError(f"Database initialization failed: {e}") from e

    async def close(self) -> None:
        """Close database connection pool."""
        async with self._lock:
            if self._pool is None:
                return

            logger.info("Closing database connection pool")
            await self._pool.close()
            self._pool = None
            logger.info("Database pool closed")

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[PoolConnectionProxy]:
        """Acquire database connection from pool."""
        if self._pool is None:
            await self.initialize()

        assert self._pool is not None  # For type checker

        try:
            async with self._pool.acquire() as connection:
                yield connection
        except Exception as e:
            logger.error("Database connection error", error=str(e))
            raise DatabaseError(f"Database operation failed: {e}") from e

    async def health_check(self) -> bool:
        """Check database connectivity and pool health."""
        try:
            async with self.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return bool(result == 1)
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False

    @property
    def is_initialized(self) -> bool:
        """Check if database pool is initialized."""
        return self._pool is not None


# Global database manager instance
db_manager = DatabaseManager()


async def get_connection() -> AsyncGenerator[PoolConnectionProxy]:
    """Get database connection for MCP tool operations."""
    async with db_manager.acquire() as conn:
        yield conn


async def initialize_database() -> None:
    """Initialize database connection pool."""
    await db_manager.initialize()


async def close_database() -> None:
    """Close database connection pool."""
    await db_manager.close()


async def health_check() -> bool:
    """Check database health."""
    return await db_manager.health_check()
