# Project Kaizen MCP Server - Claude Instructions

MCP server-specific development guidelines and type safety requirements.

## Python Type Safety Best Practices

**Context**: During CHUNK 4 implementation, we encountered multiple type checking issues that required systematic fixes. These guidelines prevent similar issues in future development.

### 1. Explicit Type Annotations

Always provide explicit type annotations for complex data structures:

```python
# ❌ Bad - Type checker can't infer
namespaces = {}
params = []
set_clauses = []

# ✅ Good - Explicit type annotations  
namespaces: dict[str, NamespaceInfo] = {}
params: list[Any] = []
set_clauses: list[str] = []
```

**Why**: Prevents "partially unknown" type errors and improves IDE autocomplete.

### 2. Type Stub Management

**Required Development Dependencies:**
```toml
[dependency-groups]
dev = [
    "asyncpg-stubs>=0.30.2",  # Type stubs for asyncpg
    # Add other stub packages as needed
]
```

**Installation Process:**
- Install type stubs for all third-party libraries during initial setup
- Document stub requirements in project documentation
- Update stubs when upgrading corresponding runtime libraries

### 3. Model Field Validation

**Never assume model fields exist without verification:**

```python
# ❌ Wrong - Assumes field exists
if hasattr(input, 'task_size') and input.task_size:
    task_size_value = input.task_size.value

# ✅ Correct - Check model definition first
# Only reference fields that actually exist in the Pydantic model
```

**Process:**
1. Always check actual Pydantic model definitions
2. Cross-reference with MCP protocol specifications
3. Validate field existence before runtime checks

### 4. AsyncPG Connection Patterns

**Correct database connection usage:**

```python
# ❌ Wrong - get_connection() returns AsyncGenerator
async with get_connection() as conn:

# ✅ Correct - Use db_manager.acquire()
async with db_manager.acquire() as conn:
```

**Database Query Validation:**
```python
# ❌ Dangerous - fetchrow() can return None
result = await conn.fetchrow(query, param)
value = result["id"]  # Potential error

# ✅ Safe - Always validate nullable results
result = await conn.fetchrow(query, param)
if not result:
    raise ValueError("Query returned no results")
value = result["id"]
```

### 5. Type Checking Workflow

**Required validation sequence before any commit:**

```bash
# 1. Strict type checking (must pass with zero errors)
uv run mypy src/ --strict

# 2. Code formatting and linting (auto-fix issues)
uv run ruff check src/ --fix

# 3. Manual IDE verification (Pylance warnings)
# Check for any remaining type warnings in VSCode
```

**Zero-tolerance policy**: All type errors must be resolved before committing.

### 6. Dynamic Query Building

**Safe parameter handling:**

```python
# Build dynamic queries with proper type safety
set_clauses: list[str] = []
params: list[Any] = []
param_count = 0

if input.new_name:
    param_count += 1
    set_clauses.append(f"name = ${param_count}")
    params.append(input.new_name)

# Always validate non-empty clauses
if not set_clauses:
    raise ValueError("No fields to update")
```

### 7. Error Prevention Checklist

**Before implementing any database operation:**
- [ ] Check Pydantic model definitions for actual fields
- [ ] Validate all fetchrow() results before indexing
- [ ] Use explicit type annotations for collections
- [ ] Install and verify type stubs for external libraries
- [ ] Test with `mypy --strict` during development
- [ ] Resolve all Pylance warnings in IDE

### 8. Common Type Issues and Solutions

**Issue**: `dict[Unknown, Unknown]` type errors
**Solution**: Add explicit type annotation: `results: dict[str, dict[str, str]] = {}`

**Issue**: `Type of "append" is partially unknown`
**Solution**: Add list type annotation: `validated: list[str] = []`

**Issue**: `Stub file not found for "library"`
**Solution**: Install type stubs: `uv add library-stubs --group dev`

**Issue**: `Value of type "Record | None" is not indexable`
**Solution**: Validate result before access:
```python
result = await conn.fetchrow(query)
if not result:
    raise ValueError("No results found")
value = result["field"]
```

## MCP Tool Implementation Standards

### FastMCP Decorator Pattern
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("project-kaizen")

@mcp.tool()
async def tool_name(input: InputModel) -> OutputModel:
    """Tool description matching MCP protocol."""
    # Implementation with proper error handling
```

### Database Integration Pattern
```python
async with db_manager.acquire() as conn:
    # Direct SQL execution with proper validation
    result = await conn.fetchrow(query, *params)
    if not result:
        raise ValueError("Operation failed")
    return ProcessedOutput(...)
```

### Logging Integration
```python
from ..utils.logging import log_mcp_tool_call, log_database_operation, log_error_with_context

# Log tool invocation
log_mcp_tool_call("tool_name", param1=value1, param2=value2)

# Log database operations  
log_database_operation("SELECT", query="operation_name", params=params)

# Log errors with context
try:
    # Operation
except Exception as e:
    log_error_with_context(e, {"tool": "tool_name", "input": input.model_dump()})
    raise
```

## Validation Requirements

- **Type Safety**: All files must pass `mypy --strict` with zero errors
- **Code Quality**: All files must pass `ruff check` with zero issues
- **IDE Compliance**: Address all Pylance warnings (not just mypy)
- **Model Validation**: Cross-reference all Pydantic models with MCP protocol
- **Database Safety**: Validate all nullable database results before use
- **Error Handling**: Comprehensive exception handling with structured logging
