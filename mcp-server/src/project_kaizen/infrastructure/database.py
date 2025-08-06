"""Database connection pool management."""

import logging
import asyncpg

logger = logging.getLogger("project-kaizen")


class DatabasePool:
    """Manages PostgreSQL connection pool lifecycle."""

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def initialize(
        self,
        db_url: str,
        db_user: str,
        db_password: str,
        db_name: str,
    ) -> None:
        """Initialize connection pool."""
        if db_url.startswith("postgresql://"):
            connection_url = db_url
        else:
            connection_url = f"postgresql://{db_user}:{db_password}@{db_url}/{db_name}"

        try:
            self._pool = await asyncpg.create_pool(
                connection_url, min_size=1, max_size=5
            )
            logger.info(
                f"Connected to PostgreSQL pool: {connection_url.split('@')[0]}@{connection_url.split('@')[1]}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

        # Verify connection
        try:
            async with self._pool.acquire() as conn:
                await conn.execute("SELECT 1")
            logger.info("Database connection verified")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            await self._pool.close()
            raise

    def get_pool(self) -> asyncpg.Pool:
        """Get the connection pool."""
        if self._pool is None:
            raise RuntimeError(
                "Database pool not initialized. Call initialize() first."
            )
        return self._pool

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Database pool closed")


# Global instance
_database_pool = DatabasePool()


def get_database_pool() -> DatabasePool:
    """Get the global database pool instance."""
    return _database_pool
