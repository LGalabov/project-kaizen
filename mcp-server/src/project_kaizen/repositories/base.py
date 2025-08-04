"""Base repository class with common database patterns."""

import asyncpg
from typing import Any

from ..infrastructure.database import get_database_pool


class BaseRepository:
    """Base repository with common database operations."""
    
    def __init__(self) -> None:
        self._db_pool = get_database_pool()
    
    async def _execute_query(self, query: str, *params: Any) -> None:
        """Execute a query without returning results."""
        pool = self._db_pool.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(query, *params)
    
    async def _fetch_one(self, query: str, *params: Any) -> asyncpg.Record | None:
        """Fetch a single row."""
        pool = self._db_pool.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *params)
    
    async def _fetch_all(self, query: str, *params: Any) -> list[asyncpg.Record]:
        """Fetch all rows."""
        pool = self._db_pool.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *params)
