# Project Kaizen MCP Server - Architecture

## Overview
Modern MCP server using FastMCP pattern with structured organization for complex requirements.

## Architecture
**Structured FastMCP**: FastMCP + AsyncPG + PostgreSQL + UV Package Manager + Python 3.13

## Dependencies
```toml
dependencies = [
    "mcp[cli]>=1.12.2",    # Latest MCP SDK with CLI tools
    "asyncpg>=0.30.0",     # PostgreSQL async driver
    "structlog>=25.4.0",   # Structured logging
]
dev = [
    "pytest>=8.4.1",      # Testing framework
    "pytest-asyncio>=1.1.0",  # Async test support
]
```

## Project Structure
```
mcp-server/
├── pyproject.toml              # UV dependencies & config
├── uv.lock                     # Dependency lockfile
├── src/mcp_server/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── server.py               # FastMCP server setup
│   ├── database.py             # AsyncPG connection management
│   ├── config.py               # Pydantic settings
│   ├── models/                 # Pydantic models for MCP actions
│   │   ├── __init__.py
│   │   ├── namespace.py        # 4 namespace models
│   │   ├── scope.py            # 3 scope models
│   │   └── knowledge.py        # 5 knowledge models
│   ├── tools/                  # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── namespace.py        # 4 namespace @mcp.tool()
│   │   ├── scope.py            # 3 scope @mcp.tool()
│   │   └── knowledge.py        # 5 knowledge @mcp.tool()
│   └── utils/
│       ├── __init__.py
│       └── logging.py          # Structured logging
└── tests/
    ├── __init__.py
    ├── conftest.py            # Pytest fixtures
    ├── test_database.py       # Database tests
    ├── test_models.py         # Pydantic tests
    └── test_tools.py          # MCP tools tests
```

## Implementation Pattern
```python
from mcp.server.fastmcp import FastMCP
import asyncpg

mcp = FastMCP("project-kaizen")

@mcp.tool()
async def get_task_context(
    queries: list[str], 
    scope: str, 
    task_size: str | None = None
) -> dict:
    """Multi-query knowledge retrieval with scope inheritance"""
    async with get_db_connection() as conn:
        results = await conn.fetch(
            "SELECT * FROM get_task_context($1, $2, $3)",
            queries, scope, task_size
        )
        return process_results(results)
```

## Key Principles
1. **FastMCP Pattern**: Use `@mcp.tool()` decorators for all 12 MCP actions
2. **Direct Database Access**: AsyncPG calls directly in tools (no service layer)
3. **Minimal Abstraction**: Only abstract what's necessary for testing/config
4. **Modern Python**: Python 3.13+, type hints, Pydantic validation
5. **Production Ready**: Structured logging, error handling, configuration
6. **MCP Compliance**: Must match exact specs in protocol documentation