# MCP Server Implementation Plan

## Overview
Project Kaizen MCP server with 12 MCP actions using Structured FastMCP Architecture.
**Stack**: Python 3.10+ + FastMCP 2.1.0 + AsyncPG + PostgreSQL + UV

## Implementation Chunks

### **CHUNK 1: Project Foundation** [COMPLETED]
- `pyproject.toml` - UV dependencies configuration ✅
- `uv.lock` - Dependency lockfile ✅
- `src/project_kaizen/config.py` - Pydantic settings ✅
- Directory structure and .gitignore setup ✅
- **Test:** UV project works, config loads, dependencies resolve ✅

### **CHUNK 1.5: Architectural Foundations** [COMPLETED]
- `src/project_kaizen/types.py` - Common types, enums, constants ✅
- `src/project_kaizen/exceptions.py` - Base exception hierarchy ✅
- `.env.example` - Development environment template ✅
- Database connection validation test ✅
- Version consistency check ✅
- Project-wide trailing newline compliance ✅
- **Test:** Types importable, exceptions work, DB connection succeeds ✅

### **CHUNK 2: Core Structure** [COMPLETED]
- `src/project_kaizen/database.py` - AsyncPG connection management ✅
- `src/project_kaizen/utils/logging.py` - Structured logging setup ✅
- **Test:** Database connections work, logging outputs JSON ✅

### **CHUNK 3: Pydantic Models** [COMPLETED]
- `src/project_kaizen/models/namespace.py` - 4 namespace action models ✅
- `src/project_kaizen/models/scope.py` - 3 scope action models ✅
- `src/project_kaizen/models/knowledge.py` - 5 knowledge action models ✅
- **Test:** All Pydantic models validate per MCP specs ✅

### **CHUNK 4: MCP Tools** [COMPLETED]
- `src/project_kaizen/tools/namespace.py` - 4 namespace @mcp.tool() functions ✅
- `src/project_kaizen/tools/scope.py` - 3 scope @mcp.tool() functions ✅
- `src/project_kaizen/tools/knowledge.py` - 5 knowledge @mcp.tool() functions ✅
- **Test:** Each tool executes successfully ✅

### **CHUNK 5: FastMCP Server** [COMPLETED]
- `src/project_kaizen/server.py` - FastMCP server setup with all tools ✅
- `src/project_kaizen/__main__.py` - Entry point and configuration ✅
- **Test:** MCP server starts, all 12 tools accessible ✅

### **CHUNK 6: Testing** [PENDING]
- `tests/conftest.py` - Pytest fixtures (async, database, MCP client)
- `tests/test_database.py` - Database connection tests
- `tests/test_models.py` - Pydantic validation tests
- `tests/test_tools.py` - MCP tools integration tests
- **Test:** Full test suite passes

### **CHUNK 7: Production-Ready Server** [IN PROGRESS - Phase 7.2 Complete]

#### **Phase 7.1: Architecture Cleanup** [COMPLETED]
- Clean pyproject.toml from 139 lines to 25 lines ✅
- Upgrade from mcp[cli]>=1.12.2 to fastmcp>=2.1.0 ✅
- Remove structlog, keep pydantic-settings for clean dependencies ✅
- Add pyright>=1.1.389 with strict configuration for maximum type checking ✅
- **Test:** Clean architecture matches production examples ✅

#### **Phase 7.2: FastMCP Multi-transport Migration** [COMPLETED]
- Fix server.py import: `from mcp.server.fastmcp` → `from fastmcp` ✅
- Add stateless_http=True to FastMCP constructor ✅
- Create CLI in __init__.py with argparse for --transport, --host, --port ✅
- Implement transport selection logic (stdio vs http modes) ✅
- Add proper ToolAnnotations to all 12 MCP tools ✅
- Initialize AsyncPG connection pool with proper error handling ✅
- Add strict pyright type checking configuration ✅
- **Test:** Both stdio and HTTP transports work, database connectivity verified ✅

#### **Phase 7.3: Production Features** [PENDING]
- **Database connection args** - Add CLI args for database configuration ✅ (completed in Phase 7.2)
- **Tool annotations** - Add ToolAnnotations to all 12 tools with appropriate hints ✅ (completed in Phase 7.2)
- **Production Docker** - Dockerfile with UV, HTTP transport, environment variables ⚠️
- **Docker integration** - Update docker-compose.yml to add MCP server service ⚠️
- **MCP client integration test** - Test actual MCP client calling get_task_context tool ⚠️
- **Tool functionality verification** - Verify all 12 tools work with database ⚠️
- **Test:** stdio mode works locally, HTTP mode works in Docker, all tools accessible ❌

## Implementation Rules
- **Tool Pattern**: Each MCP action = one `@mcp.tool()` function
- **Database Pattern**: Direct calls to PostgreSQL functions
- **Error Pattern**: Pydantic validation + AsyncPG error handling
- **Test Pattern**: MCP protocol + database verification

## Requirements
- All 12 MCP actions per protocol specs
- Database connection pooling
- MCP protocol compliance
- Docker integration with existing PostgreSQL
