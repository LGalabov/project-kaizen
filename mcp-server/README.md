# Project Kaizen MCP Server

FastMCP server providing AI tools with persistent organizational knowledge management.

## Architecture

**FastMCP Design:**
- **Single FastMCP Instance**: One global instance controls entire lifecycle
- **Lazy Initialization**: Database connections created on-demand within tool calls
- **Clean Separation**: MCP protocol handling vs pure business logic
- **Zero Manual Async**: FastMCP manages all event loops and lifecycle

**Tech Stack:**
- **FastMCP** (MCP SDK 1.12.2) for protocol handling
- **AsyncPG** for PostgreSQL connectivity  
- **UV** for package management
- **Python 3.13** with strict type checking

## Quick Start

### Prerequisites
- Python 3.13+
- UV package manager (`brew install uv`)
- PostgreSQL database (see parent project)

### Development Setup
```bash
# Install dependencies
uv sync

# Run server (starts immediately, no pre-initialization)
uv run kaizen-mcp

# Verify - should discover 12 tools without asyncio conflicts
# Server output: "FastMCP server started" (no complex lifecycle messages)

# Type checking (must pass with zero errors)
uv run mypy src/ --strict

# Linting
uv run ruff check src/ --fix
```

### Project Structure
```
src/project_kaizen/
├── __main__.py          # Entry: mcp.run() (9 lines)
├── server.py            # Single FastMCP + all 12 @mcp.tool decorators
├── settings.py          # Pydantic configuration
├── core/                # Business logic (no FastMCP dependencies)
│   ├── database_ops.py  # Lazy database manager
│   ├── knowledge_ops.py # Knowledge operations
│   ├── namespace_ops.py # Namespace operations
│   └── scope_ops.py     # Scope operations
├── models/              # Pydantic input/output models
└── utils/logging.py     # Structured logging
```

## MCP Tools
**12 tools organized by domain:**

**Namespace Management (4 tools):**
- `get_namespaces` - Discover existing organizational structures
- `create_namespace` - Create new namespace with default scope
- `update_namespace` - Update namespace properties
- `delete_namespace` - Remove namespace and cascade delete

**Scope Management (3 tools):**  
- `create_scope` - Create new scope with parent relationships
- `update_scope` - Update scope properties and hierarchy
- `delete_scope` - Remove scope and associated knowledge

**Knowledge Management (5 tools):**
- `write_knowledge` - Store new knowledge entry
- `update_knowledge` - Modify existing knowledge
- `delete_knowledge` - Remove knowledge entry
- `resolve_knowledge_conflict` - Handle contradictory information
- `get_task_context` - AI-powered knowledge retrieval with full-text search

## Configuration
Environment variables configured via Pydantic settings in `settings.py`:
- Database connection (PostgreSQL)
- Logging levels and structured output
- Connection pooling parameters

## Key Features
- **Instant Startup**: No complex initialization, FastMCP handles everything
- **Asyncio Safe**: Single instance eliminates event loop conflicts  
- **Type Safe**: Strict mypy compliance with zero tolerance for errors
- **Lazy Loading**: Resources initialized only when needed
- **Structured Logging**: Comprehensive operation tracking
- **Full-Text Search**: PostgreSQL-powered knowledge discovery

## Development Patterns
```python
# Adding new tools - follow this pattern in server.py
@mcp.tool
async def new_tool(input: NewToolInput) -> NewToolOutput:
    log_mcp_tool_call("new_tool", **input.model_dump())
    try:
        result = await core_ops.business_function(input.param)
        return NewToolOutput(**result)
    except Exception as e:
        log_error_with_context(e, {"tool": "new_tool", "input": input.model_dump()})
        raise
```

## Documentation
- `CLAUDE.md` - AI development instructions and patterns
- `docs/` - Architecture patterns and implementation guides
