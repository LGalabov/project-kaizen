# FastMCP Server Architecture

## Implementation Overview

### Single FastMCP Instance Pattern
```python
# server.py - Single global instance with all tools
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("project-kaizen")

@mcp.tool
async def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
    result = await knowledge_ops.create_knowledge_entry(input.scope, input.content, input.context)
    return WriteKnowledgeOutput(id=result, scope=input.scope)
```

**Benefits:**
- **Single source of truth**: All tools defined in one place
- **No instance conflicts**: Single FastMCP instance eliminates asyncio conflicts
- **FastMCP controls lifecycle**: No manual event loop management
- **Clear boundaries**: MCP protocol vs business logic separation

### Minimal Entry Point
```python
# __main__.py - 9 lines total
from project_kaizen.server import mcp

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()
```

**Key Features:**
- **Zero manual async**: FastMCP manages all event loops and lifecycle
- **Instant startup**: No pre-initialization, lazy loading on tool calls
- **FastMCP standard**: Follows proven FastMCP patterns

### Package Structure
```
src/project_kaizen/
├── __init__.py          # Package marker with version
├── __main__.py          # Entry: mcp.run() (9 lines)
├── server.py            # Single FastMCP + 12 @mcp.tool decorators
├── settings.py          # Pydantic configuration  
├── py.typed             # PEP 561 type marker
├── exceptions.py        # Custom exceptions
├── types.py             # Common types/enums
├── core/                # Business logic (no FastMCP dependencies)
│   ├── __init__.py
│   ├── database_ops.py  # Lazy database manager
│   ├── knowledge_ops.py # Knowledge operations
│   ├── namespace_ops.py # Namespace operations
│   └── scope_ops.py     # Scope operations
├── models/              # Pydantic input/output models
│   ├── __init__.py
│   ├── knowledge.py     # Knowledge I/O models
│   ├── namespace.py     # Namespace I/O models
│   └── scope.py         # Scope I/O models
└── utils/
    ├── __init__.py
    └── logging.py       # Structured logging
```

## Core Patterns

### Lazy Database Initialization
```python
# core/database_ops.py
_db_manager: DatabaseManager | None = None

def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# Usage in business logic
async def create_knowledge_entry(scope: str, content: str, context: str) -> str:
    db_manager = get_db_manager()  # Lazy initialization
    async with db_manager.acquire() as conn:
        # Database operations
```

**Benefits:**
- **Faster startup**: No blocking database initialization
- **Error isolation**: Database issues don't prevent server start
- **Resource efficiency**: Connections created only when needed

### Business Logic Separation
```python
# server.py - MCP protocol handling
@mcp.tool
async def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
    log_mcp_tool_call("write_knowledge", scope=input.scope)
    try:
        knowledge_id = await knowledge_ops.create_knowledge_entry(input.scope, input.content, input.context)
        return WriteKnowledgeOutput(id=knowledge_id, scope=input.scope)
    except Exception as e:
        log_error_with_context(e, {"tool": "write_knowledge", "input": input.model_dump()})
        raise

# core/knowledge_ops.py - Pure business logic  
async def create_knowledge_entry(scope: str, content: str, context: str) -> str:
    # No MCP dependencies, pure database/business logic
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Implementation
        return knowledge_id
```

**Benefits:**
- **Testability**: Business logic can be tested independently
- **Reusability**: Core functions usable outside MCP context
- **Clarity**: Clear separation of concerns

### Tool Organization
All 12 tools organized in server.py with clear domain sections:

```python
# server.py structure
mcp = FastMCP("project-kaizen")

# === NAMESPACE TOOLS === (4 tools)
@mcp.tool
async def get_namespaces(input: GetNamespacesInput) -> GetNamespacesOutput:

@mcp.tool  
async def create_namespace(input: CreateNamespaceInput) -> CreateNamespaceOutput:

# === SCOPE TOOLS === (3 tools)
@mcp.tool
async def create_scope(input: CreateScopeInput) -> CreateScopeOutput:

# === KNOWLEDGE TOOLS === (5 tools)
@mcp.tool
async def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
```

**Benefits:**
- **Single source of truth**: All tools discoverable in one file
- **No module importing complexity**: Direct decorator usage
- **Clear organization**: Domain-based grouping with comments

## Performance Characteristics

### Startup Performance
- **Startup Time**: ~100ms (FastMCP + lazy loading)
- **Memory Usage**: Connections allocated on first tool usage
- **Error Handling**: Database failures isolated to individual tool calls

### Database Configuration
```python
# settings.py
class DatabaseConfig(BaseSettings):
    min_connections: int = Field(default=1, description="Minimum connection pool size")
    max_connections: int = Field(default=5, description="Maximum connection pool size")
```

- **Min Connections**: 1 (optimal for MCP server lazy loading)
- **Max Connections**: 5 (sufficient for concurrent MCP client load)

## Development Patterns

### Adding New Tools
1. Define Pydantic models in `models/`
2. Implement business logic in `core/`
3. Add MCP tool decorator in `server.py`
4. Follow error handling and logging patterns

### Adding New Domains
1. Create new core module (e.g., `core/analytics_ops.py`)
2. Add corresponding models (`models/analytics.py`)
3. Group tools in server.py with domain comments

### Database Schema Integration
- Business logic in `core/` modules adapts to schema changes
- No changes needed to MCP protocol layer in `server.py`
- Type safety ensures compatibility across layers

## FastMCP Best Practices

### Core Principles
1. **FastMCP is the runtime**: Don't manage it, let it manage your application
2. **Single instance rule**: Never create multiple FastMCP instances
3. **Lazy initialization**: Initialize resources on-demand within tool calls
4. **Minimal entry points**: Just `mcp.run()` in `__main__.py`
5. **Business logic separation**: Pure functions in separate modules

### Error Handling Pattern
```python
@mcp.tool
async def tool_name(input: InputModel) -> OutputModel:
    log_mcp_tool_call("tool_name", **input.model_dump())
    try:
        result = await core_ops.business_function(input.param)
        return OutputModel(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "tool_name", "input": input.model_dump()})
        raise
```

### Type Safety Requirements
```bash
# Required validation sequence
uv run mypy src/ --strict      # Must pass with zero errors
uv run ruff check src/ --fix   # Auto-fix linting issues
```

All tools must pass strict type checking with zero tolerance for errors.
