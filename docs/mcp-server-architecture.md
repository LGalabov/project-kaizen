# MCP Server Architecture Specification

## Table of Contents
- [Technology Stack](#technology-stack)
- [Architecture Design](#architecture-design)
- [Database Integration](#database-integration)
- [MCP Server Implementation](#mcp-server-implementation)
- [Docker Architecture](#docker-architecture)
- [Environment Configuration](#environment-configuration)
- [AI Client Integration](#ai-client-integration)
- [Performance Characteristics](#performance-characteristics)
- [Development Benefits](#development-benefits)

## Technology Stack

### Primary Choice: Python with FastAPI

**Framework Stack:**
```python
# Core Framework
FastAPI              # Async web framework with automatic OpenAPI docs
asyncpg             # High-performance async PostgreSQL driver
pydantic            # Data validation/serialization (included with FastAPI)
structlog           # Structured logging for debugging complex queries

# MCP Integration
mcp-python          # Official MCP server SDK from Anthropic
```

**Why Python Wins for This Use Case:**

1. **MCP Ecosystem Leadership**: Python has the most mature MCP libraries and examples from Anthropic
2. **Database-Heavy Workload**: Excellent PostgreSQL integration with `asyncpg` for async performance
3. **AI Integration**: Natural fit for AI ecosystem, better Claude Code integration
4. **Complex Query Logic**: Python's expressiveness handles our sophisticated search logic elegantly
5. **Rapid Development**: Fast iteration for the complex knowledge management domain logic

## Architecture Design

### Service Structure
```
mcp-server/
├── app/
│   ├── main.py              # FastAPI app + MCP server initialization
│   ├── database/
│   │   ├── connection.py    # AsyncPG connection pool
│   │   └── queries.py       # Complex PostgreSQL queries
│   ├── mcp/
│   │   ├── actions.py       # MCP action implementations  
│   │   └── models.py        # Pydantic models for MCP protocol
│   ├── services/
│   │   ├── knowledge.py     # Knowledge management business logic
│   │   ├── search.py        # Multi-query search orchestration
│   │   └── scope.py         # Namespace/scope hierarchy logic
│   └── config.py            # Environment-based configuration
├── docker/
│   └── Dockerfile           # Multi-stage Python build
├── docker-compose.yml       # Integration with PostgreSQL
└── .env.example             # Environment variable template
```

## Database Integration

### Connection Management
```python
import asyncpg
from contextlib import asynccontextmanager
import os

class DatabaseManager:
    def __init__(self):
        self.pool: asyncpg.Pool = None
    
    async def initialize(self):
        database_url = os.getenv("DATABASE_URL", "postgresql://kaizen_user:kaizen_passw0rd@localhost:5432/kaizen_knowledge")
        self.pool = await asyncpg.create_pool(
            database_url,
            min_size=int(os.getenv("DB_POOL_MIN_SIZE", "2")),
            max_size=int(os.getenv("DB_POOL_MAX_SIZE", "10")),
            command_timeout=int(os.getenv("DB_COMMAND_TIMEOUT", "30"))
        )
    
    @asynccontextmanager
    async def get_connection(self):
        async with self.pool.acquire() as conn:
            yield conn
```

### Query Integration
```python
async def get_task_context(
    query_terms: List[str], 
    target_scope: str, 
    filter_task_size: Optional[str] = None
) -> List[KnowledgeResult]:
    async with db.get_connection() as conn:
        results = await conn.fetch(
            "SELECT * FROM get_task_context($1, $2, $3)",
            query_terms, target_scope, filter_task_size
        )
        return [KnowledgeResult.from_row(r) for r in results]
```

## MCP Server Implementation

### Core Server Setup
```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import os

# Environment-based server configuration
server_name = os.getenv("MCP_SERVER_NAME", "project-kaizen")
app = Server(server_name)

@app.call_tool()
async def get_task_context(
    queries: List[str],
    scope: str,
    task_size: Optional[str] = None
) -> List[TextContent]:
    """Multi-query knowledge retrieval with scope inheritance"""
    results = await search_service.get_task_context(
        query_terms=queries,
        target_scope=scope, 
        filter_task_size=task_size
    )
    
    return [
        TextContent(
            type="text",
            text=f"Scope: {r.qualified_scope_name}\nContent: {r.content}\nRelevance: {r.relevance_rank}"
        ) for r in results
    ]
```

### MCP Action Implementations

**Core Actions Required:**
- `get_task_context` - Multi-query knowledge retrieval
- `write_knowledge` - Store new knowledge entries
- `update_knowledge` - Update existing knowledge
- `delete_knowledge` - Remove knowledge entries
- `create_namespace` - Namespace management
- `create_scope` - Scope management
- `resolve_knowledge_conflict` - Conflict resolution

## Docker Architecture

### Multi-Stage Dockerfile
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage  
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check endpoint
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "app.main"]
```

### Docker Compose Integration
```yaml
services:
  kaizen-postgres:
    image: postgres:17
    container_name: kaizen-db
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-kaizen_knowledge}
      POSTGRES_USER: ${POSTGRES_USER:-kaizen_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-kaizen_password}
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "${POSTGRES_HOST_PORT:-5453}:5432"
    volumes:
      - kaizen_data:/var/lib/postgresql/data/pgdata
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./database/test/sample-data.sql:/docker-entrypoint-initdb.d/02-sample-data.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-kaizen_user} -d ${POSTGRES_DB:-kaizen_knowledge}"]
      interval: ${POSTGRES_HEALTH_INTERVAL:-10s}
      timeout: ${POSTGRES_HEALTH_TIMEOUT:-5s}
      retries: ${POSTGRES_HEALTH_RETRIES:-5}
    restart: unless-stopped
    
  kaizen-mcp-server:
    build: .
    container_name: kaizen-mcp
    environment:
      # Database Connection
      DATABASE_URL: "postgresql://${POSTGRES_USER:-kaizen_user}:${POSTGRES_PASSWORD:-kaizen_password}@kaizen-postgres:5432/${POSTGRES_DB:-kaizen_knowledge}"
      DATABASE_HOST: ${DATABASE_HOST:-kaizen-postgres}
      DATABASE_PORT: ${DATABASE_PORT:-5432}
      DATABASE_NAME: ${POSTGRES_DB:-kaizen_knowledge}
      DATABASE_USER: ${POSTGRES_USER:-kaizen_user}
      DATABASE_PASSWORD: ${POSTGRES_PASSWORD:-kaizen_password}
      
      # MCP Server Configuration
      MCP_SERVER_NAME: ${MCP_SERVER_NAME:-project-kaizen}
      MCP_SERVER_HOST: ${MCP_SERVER_HOST:-0.0.0.0}
      MCP_SERVER_PORT: ${MCP_SERVER_PORT:-5452}
      
      # Application Settings
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      DEBUG_MODE: ${DEBUG_MODE:-false}
      
      # Database Pool Configuration
      DB_POOL_MIN_SIZE: ${DB_POOL_MIN_SIZE:-2}
      DB_POOL_MAX_SIZE: ${DB_POOL_MAX_SIZE:-10}
      DB_COMMAND_TIMEOUT: ${DB_COMMAND_TIMEOUT:-30}
      DB_CONNECTION_TIMEOUT: ${DB_CONNECTION_TIMEOUT:-10}
      
      
    ports:
      - "${MCP_HOST_PORT:-5452}:${MCP_SERVER_PORT:-5452}"
    depends_on:
      kaizen-postgres:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${MCP_SERVER_PORT:-5452}/health"]
      interval: ${MCP_HEALTH_INTERVAL:-30s}
      timeout: ${MCP_HEALTH_TIMEOUT:-10s}
      retries: ${MCP_HEALTH_RETRIES:-3}
      start_period: ${MCP_HEALTH_START_PERIOD:-10s}
    
volumes:
  kaizen_data:
    driver: local
```

## Environment Configuration

### Docker MCP Toolkit Compatible Variables

All environment variables include descriptions that will appear in Docker Desktop's configuration UI:

**Core Database Settings:**
```bash
# PostgreSQL Database Name - The name of the knowledge database
POSTGRES_DB=kaizen_knowledge

# PostgreSQL Username - Database user for MCP server authentication  
POSTGRES_USER=kaizen_user

# PostgreSQL Password - Secure password for database access
POSTGRES_PASSWORD=kaizen_password

# PostgreSQL Host Port - External port to access PostgreSQL (avoid conflicts)
POSTGRES_HOST_PORT=5453
```

**MCP Server Configuration:**
```bash
# MCP Server Name - Identifier for the MCP server instance
MCP_SERVER_NAME=project-kaizen

# MCP Server Host Port - External port for MCP server (paired with database on 5453)
MCP_HOST_PORT=5452

# MCP Server Internal Port - Internal container port for the MCP server
MCP_SERVER_PORT=5452

# MCP Server Host - Network interface binding (0.0.0.0 for all interfaces)
MCP_SERVER_HOST=0.0.0.0
```

**Application Settings:**
```bash
# Log Level - Application logging verbosity (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Debug Mode - Enable detailed error reporting and debug features
DEBUG_MODE=false

```

**Database Performance Tuning:**
```bash
# Database Pool Min Size - Minimum number of database connections to maintain
DB_POOL_MIN_SIZE=2

# Database Pool Max Size - Maximum number of concurrent database connections
DB_POOL_MAX_SIZE=10

# Database Command Timeout - Maximum time in seconds for database queries
DB_COMMAND_TIMEOUT=30

# Database Connection Timeout - Maximum time in seconds to establish connection
DB_CONNECTION_TIMEOUT=10
```

**Health Check Configuration:**
```bash
# PostgreSQL Health Check Interval - How often to check database health
POSTGRES_HEALTH_INTERVAL=10s

# PostgreSQL Health Check Timeout - Maximum time for health check response
POSTGRES_HEALTH_TIMEOUT=5s

# PostgreSQL Health Check Retries - Number of failed checks before unhealthy
POSTGRES_HEALTH_RETRIES=5

# MCP Health Check Interval - How often to check MCP server health
MCP_HEALTH_INTERVAL=30s

# MCP Health Check Timeout - Maximum time for MCP health check response
MCP_HEALTH_TIMEOUT=10s

# MCP Health Check Retries - Number of failed checks before unhealthy
MCP_HEALTH_RETRIES=3

# MCP Health Check Start Period - Grace period before health checks begin
MCP_HEALTH_START_PERIOD=10s
```

### Complete .env.example Template
```bash
# =============================================================================
# Project Kaizen MCP Server Configuration
# =============================================================================

# Database Configuration
POSTGRES_DB=kaizen_knowledge
POSTGRES_USER=kaizen_user
POSTGRES_PASSWORD=kaizen_password
POSTGRES_HOST_PORT=5453

# Database Connection Details (Internal)
DATABASE_HOST=kaizen-postgres
DATABASE_PORT=5432
DATABASE_NAME=kaizen_knowledge
DATABASE_USER=kaizen_user
DATABASE_PASSWORD=kaizen_password
DATABASE_URL=postgresql://kaizen_user:kaizen_password@kaizen-postgres:5432/kaizen_knowledge

# MCP Server Configuration
MCP_SERVER_NAME=project-kaizen
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=5452
MCP_HOST_PORT=5452

# Application Settings
LOG_LEVEL=INFO
DEBUG_MODE=false

# Database Performance
DB_POOL_MIN_SIZE=2
DB_POOL_MAX_SIZE=10
DB_COMMAND_TIMEOUT=30
DB_CONNECTION_TIMEOUT=10

# Health Check Configuration
POSTGRES_HEALTH_INTERVAL=10s
POSTGRES_HEALTH_TIMEOUT=5s
POSTGRES_HEALTH_RETRIES=5
MCP_HEALTH_INTERVAL=30s
MCP_HEALTH_TIMEOUT=10s
MCP_HEALTH_RETRIES=3
MCP_HEALTH_START_PERIOD=10s
```

### Docker MCP Toolkit Compatibility

The environment variable approach ensures compatibility with Docker MCP toolkit requirements:

1. **Configurable Database Connection**: `DATABASE_URL` environment variable
2. **Flexible Server Settings**: All runtime parameters configurable via env vars
3. **Standard Docker Practices**: Health checks, non-root user, proper port exposure
4. **Production Ready**: Restart policies, dependency management, resource limits

## AI Client Integration

### Claude Code Connection
```json
{
  "mcpServers": {
    "project-kaizen": {
      "command": "docker",
      "args": ["run", "--rm", "--env-file", ".env", "-p", "5452:5452", "project-kaizen/mcp-server"],
      "env": {
        "DATABASE_URL": "postgresql://kaizen_user:kaizen_password@host.docker.internal:5453/kaizen_knowledge",
        "MCP_SERVER_PORT": "5452",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Key Integration Points

1. **Automatic Context Retrieval**: Claude Code calls `get_task_context()` at session start
2. **Multi-Query Intelligence**: Claude generates 3-4 targeted queries per complex task
3. **Scope Detection**: CLAUDE.md file provides automatic scope context
4. **Knowledge Storage**: Teaching sessions trigger `write_knowledge()` calls

## Performance Characteristics

### Database Performance
- **Connection Pooling**: 2-10 async connections via asyncpg (configurable)
- **Query Optimization**: Direct PostgreSQL function calls, no ORM overhead
- **Single Client Focus**: Optimized for individual developer or small team usage

### Application Performance
- **Async Throughout**: FastAPI + asyncpg for non-blocking I/O
- **Pydantic Models**: Fast serialization/validation
- **Structured Logging**: Debug complex queries without performance impact
- **Minimal Memory Footprint**: No unnecessary caching or background processes

### Scaling Strategy
- **Current Target**: Single container handles 1 primary client efficiently
- **Simple Architecture**: No complex distributed systems or microservices overhead
- **Resource Efficiency**: Designed for development environments and small teams

## Development Benefits

### Why This Stack Excels

1. **Fast Development**: Python's expressiveness + FastAPI's auto-docs accelerate development
2. **AI Ecosystem**: Natural integration with Claude Code and MCP protocol
3. **Database Mastery**: Complex PostgreSQL queries are Python's strength
4. **Containerization**: Clean Docker integration with existing PostgreSQL setup
5. **Debugging**: Excellent tooling for complex search logic troubleshooting
6. **Environment Flexibility**: Full configuration via environment variables

### Alternative Considered: Node.js/TypeScript

**Would be excellent for:**
- Teams with strong JS/TS preference
- Lighter memory footprint requirements
- JavaScript-first MCP ecosystems

**Python edges out due to:**
- Superior MCP library maturity
- Better AI ecosystem integration
- More natural fit for complex database query orchestration
- Stronger PostgreSQL async integration patterns

### Production Readiness

**Built-in Production Features:**
- Health check endpoints for container orchestration
- Structured logging with configurable levels
- Graceful shutdown handling
- Resource-aware connection pooling
- Environment-based configuration management
- Security best practices (non-root user, minimal attack surface)

This architecture provides a robust, scalable foundation for the Project Kaizen MCP server while maintaining simplicity and focus on the core mission of persistent AI knowledge management.