# FastMCP Server Architecture

## Core Principles

### Single FastMCP Instance Pattern
```python
# server.py - Global instance
from fastmcp import FastMCP

mcp = FastMCP("project-kaizen")

# tools/knowledge.py - Import and use global instance
from ..server import mcp

@mcp.tool
def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
    # Implementation
```

**Why**: FastMCP manages internal state, routing, and async lifecycle. Multiple instances create conflicts.

### Entry Point Pattern
```python
# __main__.py - Minimal entry point
from project_kaizen.server import mcp

def main():
    mcp.run()  # FastMCP handles all async lifecycle

if __name__ == "__main__":
    main()
```

**Why**: FastMCP controls the entire server lifecycle including event loops, signal handling, and protocol management.

### Package Structure
```
src/project_kaizen/
├── __init__.py
├── __main__.py          # Entry: mcp.run()
├── server.py            # Global FastMCP instance
├── config.py            # Pydantic settings
├── types.py             # Common types/enums
├── exceptions.py        # Custom exceptions
├── models/              # Pydantic models
│   ├── __init__.py
│   ├── namespace.py
│   ├── scope.py
│   └── knowledge.py
├── tools/               # MCP tool implementations
│   ├── __init__.py
│   ├── namespace.py
│   ├── scope.py
│   └── knowledge.py
├── utils/               # Shared utilities
│   ├── __init__.py
│   ├── logging.py
│   └── database.py
└── _business/           # Internal business logic
    ├── __init__.py
    ├── namespace_ops.py
    ├── scope_ops.py
    └── knowledge_ops.py
```

### Tool Organization
- **tools/**: MCP decorators + input/output handling
- **_business/**: Database operations + business logic
- **models/**: Pydantic validation models
- **utils/**: Shared infrastructure (logging, database)

### Server Lifecycle
1. **Initialization**: FastMCP creates instance
2. **Tool Discovery**: Import modules with `@mcp.tool` decorators
3. **Protocol Setup**: FastMCP handles MCP protocol compliance
4. **Event Loop**: FastMCP manages async lifecycle
5. **Shutdown**: FastMCP handles graceful cleanup

## Database Integration

### Connection Management
```python
# utils/database.py - Connection utility
class DatabaseManager:
    async def acquire(self):
        # Connection pooling logic
        
# tools/knowledge.py - Usage in tools
async with db_manager.acquire() as conn:
    result = await conn.fetchrow(query, *params)
```

### Initialization Strategy
- **Not in main()**: Database connections initialized lazily in business logic
- **Connection Pooling**: AsyncPG pool managed by DatabaseManager
- **Error Handling**: Database errors handled at tool level, not entry point

## Configuration Management

### Settings Pattern
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env"])
    
    database_host: str
    database_port: int
    log_level: str = "INFO"

settings = Settings()
```

### Environment Variables
- `.env` file for local development
- Environment variables for production
- No hardcoded configuration values

## Tool Implementation Pattern

### Decorator Usage
```python
from ..server import mcp  # Import global instance
from ..models.knowledge import WriteKnowledgeInput, WriteKnowledgeOutput

@mcp.tool
async def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
    """Store new knowledge entry."""
    # Business logic implementation
    return WriteKnowledgeOutput(id=result_id, scope=input.scope)
```

### Separation of Concerns
- **Tools**: MCP protocol handling + validation
- **Business Logic**: Database operations + domain logic
- **Models**: Input/output validation
- **Utils**: Infrastructure concerns

## Anti-Patterns (Avoid)

### ❌ Multiple FastMCP Instances
```python
# DON'T DO THIS
# tools/knowledge.py
mcp = FastMCP("knowledge")  # Creates competing instance

# tools/namespace.py  
mcp = FastMCP("namespace")  # Another competing instance
```

### ❌ Manual Async Management
```python
# DON'T DO THIS
def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_services())
    mcp.run()  # Competing event loops
```

### ❌ Database Init in Main
```python
# DON'T DO THIS
async def main():
    await db_manager.initialize()  # FastMCP should control lifecycle
    mcp.run()
```

## Key Decisions

- **Single FastMCP Instance**: Global instance in server.py, imported by tools
- **Minimal Entry Point**: Just call `mcp.run()`, no manual async
- **Lazy Database Init**: Connections initialized in business logic, not main
- **Standard Package Layout**: `src/package/` structure with `__main__.py`
- **Clear Tool Boundaries**: MCP decorators separate from business logic
