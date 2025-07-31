# Known Pitfalls & Solutions

## Asyncio Event Loop Conflicts

### The Problem
```python
# ❌ This causes "RuntimeError: Already running asyncio in this thread"
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(initialize_services())
        mcp_server = setup_server()
        mcp_server.run()  # FastMCP creates its own event loop - CONFLICT!
    finally:
        loop.run_until_complete(shutdown_services())
```

### Why It Fails
- FastMCP uses `anyio.run()` internally to manage async lifecycle
- Manual `asyncio.run()` or `loop.run_until_complete()` creates competing event loops
- Error: `"Cannot run the event loop while another loop is running"`

### ✅ Solution
```python
# Let FastMCP handle ALL async lifecycle
def main():
    mcp.run()  # FastMCP manages everything

if __name__ == "__main__":
    main()
```

### Database Initialization
```python
# ❌ Wrong: Initialize in main entry point
async def main():
    await db_manager.initialize()  # Competes with FastMCP
    mcp.run()

# ✅ Correct: Initialize lazily in business logic
@mcp.tool
async def write_knowledge(input: WriteKnowledgeInput):
    async with db_manager.acquire() as conn:  # Lazy initialization
        # Tool implementation
```

## Multiple FastMCP Instances

### The Problem
```python
# ❌ Each tool module creates its own FastMCP instance
# tools/knowledge.py
mcp = FastMCP("project-kaizen")

# tools/namespace.py  
mcp = FastMCP("project-kaizen")

# tools/scope.py
mcp = FastMCP("project-kaizen")
```

### Why It Fails
- Multiple instances compete for protocol handling
- Tools become isolated from each other
- Server startup becomes unpredictable
- Resource conflicts and routing issues

### ✅ Solution
```python
# server.py - Single global instance
mcp = FastMCP("project-kaizen")

# tools/knowledge.py - Import global instance
from ..server import mcp

@mcp.tool
async def write_knowledge(input: WriteKnowledgeInput):
    # Implementation
```

## Import Side-Effects & Type Checking

### The Problem
```python
# ❌ Type checker flags "unused imports"
from .tools import knowledge, namespace, scope  # "Import not accessed"
```

### Why It Happens
- Imports are needed for side-effects (tool registration)
- Type checkers don't understand decorator registration patterns
- `# noqa: F401` comments don't work consistently

### ✅ Solution
```python
# Explicitly reference imports to satisfy type checker
from .tools import knowledge, namespace, scope

def setup_server() -> FastMCP:
    # Reference imported modules
    tool_modules = [knowledge, namespace, scope]
    logger.info("Loaded tool modules", count=len(tool_modules))
    return mcp
```

## Reserved Parameter Names in Logging

### The Problem
```python
# ❌ "event" conflicts with structlog internals
logger.info("Server starting", event="server_setup")  # Parameter conflict
```

### Why It Fails
- `event`, `level`, `timestamp` are reserved by structlog/logging systems
- Creates parameter assignment conflicts
- Error: `Parameter "event" is already assigned`

### ✅ Solution
```python
# Use descriptive, non-reserved parameter names
logger.info("Server starting", operation="server_setup")
logger.info("Database ready", action="database_init")
logger.info("Tools loaded", phase="tool_registration")
```

### Safe Parameter Names
- ✅ `operation`, `action`, `phase`, `step`
- ✅ `tool_name`, `module_name`, `error_type`
- ✅ Custom domain names: `namespace_id`, `scope_name`
- ❌ `event`, `level`, `timestamp`, `message`

## Database Query Safety

### The Problem
```python
# ❌ fetchrow() can return None - type error
result = await conn.fetchrow(query, param)
value = result["id"]  # "Value of type 'Record | None' is not indexable"
```

### Why It Fails
- AsyncPG `fetchrow()` returns `Record | None`
- Type checker correctly identifies potential None access
- Runtime error if query returns no results

### ✅ Solution
```python
# Always validate database results
result = await conn.fetchrow(query, param)
if not result:
    raise ValueError(f"Query returned no results for param: {param}")
value = result["id"]  # Safe after validation
```

## Pydantic Model Field Assumptions

### The Problem
```python
# ❌ Assuming fields exist without checking model definition
if hasattr(input, 'task_size') and input.task_size:
    task_size_value = input.task_size.value  # Field doesn't exist in model
```

### Why It Fails
- Runtime checks don't match actual Pydantic model definitions
- Type checker reports "Type of 'task_size' is unknown"
- Field might not exist in the model schema

### ✅ Solution
```python
# Check actual Pydantic model definitions first
class GetTaskContextInput(BaseModel):
    # Only reference fields that actually exist
    task_size: TaskSize | None = Field(default=None)

# Then use in code
if input.task_size:
    task_size_value = input.task_size.value  # Safe - field exists
```

## Package Structure Mistakes

### The Problem
```python
# ❌ Wrong: Entry point function doesn't match pyproject.toml
[project.scripts]
kaizen-mcp = "project_kaizen.main:main"  # Function doesn't exist

def run():  # Function name mismatch
    mcp.run()
```

### Why It Fails
- Entry point looks for `main()` function, finds `run()`
- ImportError at runtime when trying to start server
- Package installation succeeds but execution fails

### ✅ Solution
```python
# Match entry point to actual function name
[project.scripts]
kaizen-mcp = "project_kaizen.main:run"  # Correct function name

# Or use standard __main__.py pattern
[project.scripts]
kaizen-mcp = "project_kaizen.__main__:main"  # Standard pattern
```

## Type Safety Workflow Violations

### The Problem
```python
# ❌ Committing without type checking
git add .
git commit -m "feat: add new feature"  # Type errors not caught
```

### Why It Fails
- Type errors discovered at runtime, not development time
- Broken code gets committed and deployed
- Time wasted debugging issues that type checking would catch

### ✅ Solution (Pre-commit Checklist)
```bash
# Required validation sequence
uv run mypy src/ --strict      # Must pass with zero errors
uv run ruff check src/ --fix   # Auto-fix linting issues
# Check IDE for any remaining Pylance warnings
git add .
git commit -m "feat: add feature"
```

## Configuration Management Mistakes

### The Problem
```python
# ❌ Hardcoded values scattered throughout code
DATABASE_HOST = "localhost"        # In database.py
LOG_LEVEL = "INFO"                # In logging.py  
DEFAULT_TIMEOUT = 30              # In client.py
```

### Why It Fails
- Configuration changes require code changes
- Different values needed for different environments
- No single source of truth for configuration

### ✅ Solution
```python
# Centralized Pydantic settings with .env support
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env"])
    
    database_host: str
    log_level: str = "INFO"
    default_timeout: int = 30

settings = Settings()  # Load from environment/env file
```

## Prevention Strategies

### Development Workflow
1. **Read FastMCP examples** before implementing patterns
2. **Follow single instance principle** - one FastMCP per service
3. **Validate with type checker** - `mypy --strict` before every commit
4. **Test entry points** - ensure `uv run package-name` works
5. **Check file endings** - all files must end with newlines

### Code Review Checklist
- [ ] Single FastMCP instance pattern used
- [ ] No manual async lifecycle management
- [ ] Database initialization in business logic, not main
- [ ] All imports properly referenced for type checker
- [ ] No reserved parameter names in logging
- [ ] All database results validated before access
- [ ] Entry point function matches pyproject.toml
- [ ] Type checking passes with `--strict`
