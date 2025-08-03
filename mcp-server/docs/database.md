# Database Integration Decisions

## AsyncPG Driver Choice

### Why AsyncPG
- **Performance**: Fastest Python PostgreSQL driver
- **Async Native**: Built for asyncio from ground up  
- **Type Safety**: Excellent type stub support with `asyncpg-stubs`
- **Connection Pooling**: Built-in pool management
- **PostgreSQL Features**: Full support for advanced features (JSON, arrays, enums)

### vs Other Options
- **psycopg3**: Good but AsyncPG has better async performance
- **SQLAlchemy**: Too heavy for MCP server use case
- **Django ORM**: Not suitable for non-Django applications

## Connection Management Strategy

### Lazy Connection Pooling Pattern
```python
# core/database_ops.py - Lazy initialization pattern
_db_manager: DatabaseManager | None = None

def get_db_manager() -> DatabaseManager:
    """Get or create database manager with lazy initialization."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

class DatabaseManager:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        if self._pool is not None:
            return
        
        async with self._lock:
            if self._pool is not None:
                return
            
            self._pool = await asyncpg.create_pool(
                dsn=settings.database.dsn,
                min_size=settings.database.min_connections,  # 1
                max_size=settings.database.max_connections,  # 5
                command_timeout=30,
            )
    
    @asynccontextmanager
    async def acquire(self):
        if self._pool is None:
            await self.initialize()
        
        async with self._pool.acquire() as connection:
            yield connection
```

### Usage in MCP Tools
```python
# server.py - MCP tool pattern
@mcp.tool
async def write_knowledge(input: WriteKnowledgeInput) -> WriteKnowledgeOutput:
    try:
        knowledge_id = await knowledge_ops.create_knowledge_entry(input.scope, input.content, input.context)
        return WriteKnowledgeOutput(id=knowledge_id, scope=input.scope)
    except Exception as e:
        log_error_with_context(e, {"tool": "write_knowledge", "input": input.model_dump()})
        raise

# core/knowledge_ops.py - Business logic with lazy DB
async def create_knowledge_entry(scope: str, content: str, context: str) -> str:
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # Database operation
        result = await conn.fetchrow(query, *params)
        if not result:
            raise ValueError("Operation failed")
        return str(result["id"])
```

## Transaction vs Autocommit Decision

### Autocommit Approach (Selected)
- **Simplicity**: Each MCP tool operation is independent
- **MCP Pattern**: Tools are designed to be atomic operations
- **Error Handling**: Cleaner error boundaries per tool
- **Performance**: No transaction overhead for simple operations

### When to Use Transactions
```python
# For complex operations spanning multiple queries
async with db_manager.acquire() as conn:
    async with conn.transaction():
        # Multiple related operations
        namespace_id = await conn.fetchval("INSERT INTO namespaces...", name)
        scope_id = await conn.fetchval("INSERT INTO scopes...", namespace_id)
        await conn.execute("INSERT INTO scope_hierarchy...", scope_id)
```

## Database Initialization Strategy

### Lazy Initialization
- **Not in main()**: Database connections initialized on first use
- **FastMCP Compatible**: No manual async lifecycle management in entry point
- **Error Handling**: Database errors handled at tool level where they occur

### Schema Management
- **External Schema**: PostgreSQL schema in `database/01-initial-schema.sql`
- **Docker Integration**: Schema loaded via `docker-entrypoint-initdb.d/`
- **No Migrations**: Schema is versioned, not migrated (for now)

## Query Safety Patterns

### Nullable Result Validation
```python
# Always check fetchrow() results
result = await conn.fetchrow(query, param)
if not result:
    raise ValueError(f"Resource not found: {param}")
value = result["field"]  # Safe after validation
```

### Parameter Safety
```python
# Use parameterized queries, never string formatting
query = "SELECT * FROM knowledge WHERE scope_id = $1 AND content LIKE $2"
results = await conn.fetch(query, scope_id, f"%{search_term}%")

# Never do: f"SELECT * FROM knowledge WHERE content LIKE '%{search_term}%'"
```

### Dynamic Query Building
```python
def build_update_query(input: UpdateKnowledgeInput) -> tuple[str, list[Any]]:
    set_clauses: list[str] = []
    params: list[Any] = []
    param_count = 0

    if input.content:
        param_count += 1
        set_clauses.append(f"content = ${param_count}")
        params.append(input.content)
    
    if not set_clauses:
        raise ValueError("No fields to update")
    
    query = f"UPDATE knowledge SET {', '.join(set_clauses)} WHERE id = ${param_count + 1}"
    params.append(input.id)
    
    return query, params
```

## Error Handling Strategy

### Database Error Categories
```python
try:
    result = await conn.fetchrow(query, *params)
except asyncpg.UniqueViolationError:
    raise ValueError(f"Resource already exists: {identifier}")
except asyncpg.ForeignKeyViolationError:
    raise ValueError(f"Referenced resource not found: {foreign_key}")
except asyncpg.PostgresError as e:
    log_error_with_context(e, {"query": query, "params": params})
    raise ValueError(f"Database operation failed: {e}")
```

### Logging Integration
```python
from ..utils.logging import log_database_operation, log_error_with_context

# Log successful operations
log_database_operation("INSERT", query="write_knowledge", params=[scope_id])

# Log errors with context
except Exception as e:
    log_error_with_context(e, {"tool": "write_knowledge", "input": input.model_dump()})
    raise
```

## Configuration Management

### Database Settings
```python
# settings.py
class DatabaseConfig(BaseModel):
    host: str
    port: int = 5432
    database: str
    user: str
    password: str
    min_connections: int = Field(default=1, description="Minimum connection pool size")
    max_connections: int = Field(default=5, description="Maximum connection pool size")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env"])
    database: DatabaseConfig
```

### Environment Variables
```bash
# .env
DATABASE__HOST=localhost
DATABASE__PORT=5453
DATABASE__DATABASE=kz_knowledge
DATABASE__USER=kz_user
DATABASE__PASSWORD=kz_password
DATABASE__MIN_CONNECTIONS=1
DATABASE__MAX_CONNECTIONS=5
```

## Performance Considerations

### Connection Pool Sizing
- **Min Connections**: 1 (optimal for MCP server lazy loading)
- **Max Connections**: 5 (sufficient for concurrent MCP client load)
- **Production**: Scale based on concurrent MCP client load

### Query Optimization
- **Indexes**: PostgreSQL schema includes optimized indexes
- **Full-text Search**: Uses PostgreSQL tsvector for knowledge search
- **Materialized Views**: Pre-computed views for complex queries

### Prepared Statements
```python
# AsyncPG automatically prepares frequently used queries
# No manual preparation needed for MCP tool patterns
```

## Testing Strategy

### Test Database Setup
```python
# tests/conftest.py
@pytest.fixture
async def test_db():
    # Create test database connection
    conn = await asyncpg.connect(TEST_DATABASE_URL)
    
    # Load schema
    with open("database/01-initial-schema.sql") as f:
        await conn.execute(f.read())
    
    yield conn
    await conn.close()
```

### Database Test Patterns
```python
async def test_write_knowledge(test_db):
    # Test database operations directly
    result = await test_db.fetchrow(
        "INSERT INTO knowledge (scope_id, content, context) VALUES ($1, $2, $3) RETURNING id",
        1, "test content", "test context"
    )
    assert result["id"] is not None
```

## Schema Integration

### Table Design
- **BIGINT PKs**: Performance over UUIDs
- **Generated Columns**: Automatic tsvector for search
- **Constraints**: Database-level validation
- **Triggers**: Automatic materialized view refresh

### Custom Types
```sql
CREATE TYPE task_size_enum AS ENUM ('XS', 'S', 'M', 'L', 'XL');
CREATE TYPE config_type_enum AS ENUM ('text', 'integer', 'float', 'boolean', 'regconfig');
```

### Functions Integration
```python
# Use PostgreSQL functions for complex operations
result = await conn.fetchrow(
    "SELECT * FROM get_task_context($1, $2, $3)",
    query_terms, target_scope, filter_task_size
)
```
