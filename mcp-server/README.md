# Project Kaizen MCP Server

Model Context Protocol server providing AI tools with persistent organizational knowledge.

## Architecture
- **FastMCP** (MCP SDK 1.12.2) for protocol handling
- **AsyncPG** for PostgreSQL connectivity
- **UV** for package management
- **Python 3.13** with modern type hints

## Quick Start

### Prerequisites
- Python 3.13+
- UV package manager (`brew install uv`)
- PostgreSQL database (see parent project)

### Development Setup
```bash
# Install dependencies
uv sync

# Run server
uv run mcp-server

# Run tests
uv run pytest
```

### Project Structure
```
src/mcp_server/
├── main.py          # Entry point
├── server.py        # FastMCP server
├── database.py      # Database connections
├── config.py        # Settings
├── models/          # Pydantic models
├── tools/           # MCP tool implementations
└── utils/           # Logging utilities
```

## MCP Actions
Implements 12 MCP actions:
- **Namespace**: get_namespaces, create_namespace, update_namespace, delete_namespace
- **Scope**: create_scope, update_scope, delete_scope
- **Knowledge**: write_knowledge, update_knowledge, delete_knowledge, resolve_knowledge_conflict
- **Search**: get_task_context

## Configuration
Environment variables configured via Pydantic settings in `config.py`.

## Development
See `TODO.md` for implementation progress and `DECISIONS.md` for architecture details.