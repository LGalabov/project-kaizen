# Development Tooling & Workflow

## Package Manager: UV

### Why UV
- **Speed**: 10-100x faster than pip for installation and resolution
- **Lock Files**: Deterministic dependencies with `uv.lock`
- **Python Management**: Built-in Python version management
- **Workspace Support**: Multi-package workspace support
- **Modern Standards**: pyproject.toml native, PEP 621 compliant

### Project Configuration
```toml
# pyproject.toml
[project]
name = "project-kaizen"
requires-python = ">=3.13"
dependencies = [
    "mcp>=1.12.2",
    "asyncpg>=0.30.2",
    "structlog>=25.4.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.4.1",
    "pytest-asyncio>=1.1.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "asyncpg-stubs>=0.30.2",
]

[project.scripts]
project-kaizen-mcp = "project_kaizen.__main__:main"
```

### Common Commands
```bash
# Install dependencies
uv sync

# Add runtime dependency
uv add fastmcp

# Add development dependency  
uv add --group dev pytest

# Run application
uv run project-kaizen-mcp

# Run tests
uv run pytest

# Type checking
uv run mypy src/ --strict

# Linting
uv run ruff check src/ --fix
```

## Type Checking: mypy

### Configuration
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
```

### Required Stubs
```toml
[dependency-groups]
dev = [
    "asyncpg-stubs>=0.30.2",    # AsyncPG type definitions
    "types-requests",           # If using requests
    # Add other stub packages as needed
]
```

### Workflow Integration
```bash
# Must pass before every commit
uv run mypy src/ --strict

# Expected output: "Success: no issues found"
# Fix ALL issues before proceeding
```

## Linting & Formatting: Ruff

### Configuration
```toml
# pyproject.toml
[tool.ruff]
target-version = "py313"
line-length = 88
src = ["src"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings  
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Usage
```bash
# Check and auto-fix issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/

# Check without fixing
uv run ruff check src/
```

## Testing: pytest

### Configuration
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
]
asyncio_mode = "auto"
```

### Test Structure
```
tests/
├── conftest.py              # Pytest fixtures
├── test_database.py         # Database connection tests
├── test_models.py           # Pydantic validation tests
├── test_tools.py            # MCP tools integration tests
└── test_server.py           # Server startup tests
```

### Fixture Patterns
```python
# tests/conftest.py
import pytest
import asyncpg
from project_kaizen.config import settings

@pytest.fixture
async def db_connection():
    """Provide test database connection."""
    conn = await asyncpg.connect(
        host=settings.database.host,
        port=settings.database.port,
        database="test_" + settings.database.database,
        user=settings.database.user,
        password=settings.database.password,
    )
    
    # Load schema
    with open("../database/schema.sql") as f:
        await conn.execute(f.read())
    
    yield conn
    
    # Cleanup
    await conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    await conn.close()

@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    monkeypatch.setenv("DATABASE__DATABASE", "test_kz_knowledge")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
```

## Pre-commit Validation

### File Requirements
- **Newline Termination**: All files must end with trailing newline
- **Encoding**: UTF-8 encoding for all text files
- **Line Endings**: Unix line endings (LF, not CRLF)

### Validation Workflow
```bash
# Before any commit - REQUIRED SEQUENCE
uv run mypy src/ --strict      # Must pass with zero errors
uv run ruff check src/ --fix   # Auto-fix any issues
uv run pytest                  # Run test suite

# Check file endings manually
find src/ -name "*.py" -exec tail -c 1 {} \; | grep -v -q "^$" && echo "Missing newlines found"

# Then commit
git add .
git commit -m "feat: add feature"
```

### Git Hooks (Optional)
```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Running pre-commit validation..."

uv run mypy src/ --strict
if [ $? -ne 0 ]; then
    echo "❌ Type checking failed"
    exit 1
fi

uv run ruff check src/
if [ $? -ne 0 ]; then
    echo "❌ Linting failed"
    exit 1
fi

echo "✅ Pre-commit validation passed"
```

## IDE Configuration

### VSCode Settings
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.mypyArgs": ["--strict"],
    "python.formatting.provider": "ruff",
    "python.linting.ruffEnabled": true,
    "files.insertFinalNewline": true,
    "files.trimFinalNewlines": true
}
```

### Recommended Extensions
- **Python**: ms-python.python
- **Pylance**: ms-python.vscode-pylance (for type checking)
- **Ruff**: charliermarsh.ruff (for linting/formatting)
- **Even Better TOML**: tamasfe.even-better-toml

## Deployment Considerations

### Docker Integration
```dockerfile
# Dockerfile
FROM python:3.13-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/

# Set entry point
CMD ["uv", "run", "project-kaizen-mcp"]
```

### Environment Management
```bash
# Development
cp .env.example .env
# Edit .env with local values

# Production
# Set environment variables directly
export DATABASE__HOST=prod-db-host
export DATABASE__PASSWORD=secure-password
```

## Performance Monitoring

### Logging Configuration
```python
# Structured JSON logging for production monitoring
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### Health Checks
```python
@mcp.tool
def health_check() -> dict[str, str]:
    """Check server health status."""
    try:
        # Check database connectivity
        # Check other dependencies
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Development Workflow Summary

### Daily Development
1. **Start**: `uv sync` to ensure dependencies are up to date
2. **Code**: Write code with IDE type checking enabled
3. **Test**: `uv run pytest` for specific functionality
4. **Validate**: Run full pre-commit sequence before commits
5. **Commit**: Use semantic commit messages

### Before Releases
1. **Full Test Suite**: `uv run pytest --cov=src`
2. **Type Checking**: `uv run mypy src/ --strict`
3. **Linting**: `uv run ruff check src/`
4. **Manual Testing**: Start server and test MCP tools
5. **Documentation**: Update relevant docs/ files
