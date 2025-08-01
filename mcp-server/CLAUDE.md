# Project Kaizen MCP Server - AI Instructions

## Quick Reference Links
- 📐 **Architecture**: [docs/architecture.md](docs/architecture.md) - FastMCP patterns + server structure
- 🔍 **Examples**: [docs/fastmcp-examples.md](docs/fastmcp-examples.md) - Proven project layouts
- ⚠️ **Pitfalls**: [docs/pitfalls.md](docs/pitfalls.md) - Known issues + solutions
- 🛡️ **Type Safety**: [docs/type-safety.md](docs/type-safety.md) - mypy + validation patterns
- 🗃️ **Database**: [docs/database.md](docs/database.md) - PostgreSQL + AsyncPG decisions
- 🔧 **Tooling**: [docs/tooling.md](docs/tooling.md) - Development workflow

## MCP Server Architecture

**Project Structure:**
```
src/project_kaizen/
├── __main__.py          # Entry: mcp.run() (9 lines)
├── server.py            # Single FastMCP instance + all 12 tools
├── settings.py          # Pydantic configuration
├── core/                # Business logic (lazy initialization)
│   ├── database_ops.py  # Lazy database manager
│   ├── knowledge_ops.py # Knowledge operations  
│   ├── namespace_ops.py # Namespace operations
│   └── scope_ops.py     # Scope operations
├── models/              # Pydantic input/output models
└── utils/logging.py     # Structured logging
```

**Key Architectural Principles:**
- **Single FastMCP Instance**: One global `mcp = FastMCP("project-kaizen")` in server.py
- **FastMCP Lifecycle Management**: FastMCP controls entire application lifecycle
- **Lazy Database Initialization**: Connections created on first tool call, not at startup
- **Clean Separation**: MCP protocol handling (server.py) vs business logic (core/)
- **Single Source of Truth**: All 12 tools defined in server.py

## Development Guidelines

**Core Principles:**
- **FastMCP is the runtime**: Don't manage it, let it manage you
- **Lazy initialization**: Services initialize on-demand within tool calls
- **Pure business logic**: core/ modules have no FastMCP dependencies
- **Single source of truth**: All tools defined in server.py with @mcp.tool decorators

**Database Pattern:**
```python
# core/database_ops.py - Lazy pattern
_db_manager: DatabaseManager | None = None

def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
```

**Tool Pattern:**
```python
# server.py - All tools in one file
@mcp.tool
async def tool_name(input: InputModel) -> OutputModel:
    log_mcp_tool_call("tool_name", **input.model_dump())
    try:
        result = await core_ops.business_function(input.param1, input.param2)
        return OutputModel(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "tool_name", "input": input.model_dump()})
        raise
```

**Pre-commit Requirements:**
```bash
uv run mypy src/ --strict      # Must pass with zero errors
uv run ruff check src/ --fix   # Auto-fix linting issues
```

**Server Testing:**
```bash
uv run kaizen-mcp              # Should start without asyncio conflicts
# Expected output: Server starts cleanly, discovers 12 tools
```

## MCP Tool Development

**12 Tools Organized by Domain:**
- **Namespace Tools (4)**: `get_namespaces`, `create_namespace`, `update_namespace`, `delete_namespace`
- **Scope Tools (3)**: `create_scope`, `update_scope`, `delete_scope`  
- **Knowledge Tools (5)**: `write_knowledge`, `update_knowledge`, `delete_knowledge`, `resolve_knowledge_conflict`, `get_task_context`

**Adding New Tools:**
1. Define Pydantic models in `models/`
2. Implement business logic in `core/`
3. Add MCP tool decorator in `server.py`
4. Follow error handling and logging patterns

**Database Configuration:**
- `min_connections: 1` - Optimal for MCP server lazy loading
- `max_connections: 5` - Sufficient for concurrent MCP client load
- Lazy initialization on first tool call

## Type Safety & Validation

**Strict Requirements:**
- All code must pass `uv run mypy src/ --strict` with zero errors
- No type: ignore comments allowed
- Explicit type annotations for all functions
- Proper nullable result validation

**Database Safety:**
```python
# Always validate database results
result = await conn.fetchrow(query, param)
if not result:
    raise ValueError(f"Query returned no results for param: {param}")
value = result["id"]  # Safe after validation
```

## Common Patterns

**Error Handling:**
```python
try:
    result = await business_function()
    return SuccessOutput(**result)
except Exception as e:
    log_error_with_context(e, {"tool": "tool_name", "input": input.model_dump()})
    raise
```

**Logging:**
```python
from ..utils.logging import log_mcp_tool_call, log_error_with_context

log_mcp_tool_call("tool_name", param1=value1, param2=value2)
```

For general project guidelines (git commits, planning, etc.), see: `../CLAUDE.md`
