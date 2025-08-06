.PHONY: help install dev lint type-check test all clean run

# Default target - show help
help:
	@echo "Project Kaizen MCP Server - Build Commands"
	@echo ""
	@echo "  make install    - Install production dependencies"
	@echo "  make dev        - Install all dependencies including dev tools"
	@echo "  make lint       - Run linting checks with ruff"
	@echo "  make type-check - Run mypy static type checking"
	@echo "  make test       - Run tests"
	@echo "  make all        - Run lint, type-check, and test"
	@echo "  make clean      - Remove build artifacts and caches"
	@echo "  make run        - Run MCP server with STDIO transport"

# Install production dependencies
install:
	uv pip install -e .

# Install development dependencies
dev:
	uv pip install -e ".[dev]"

# Run linting checks
lint:
	ruff check src/

# Run static type checking
type-check:
	mypy src/project_kaizen --strict

# Run tests
test:
	pytest tests/ -v

# Run all checks (CI/CD pipeline)
all: lint type-check test

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/

# Run MCP server with STDIO transport
run:
	python -m project_kaizen
