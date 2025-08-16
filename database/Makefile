# KaizenMCP Database Migration Makefile
# Provides convenient commands for database operations

.PHONY: help migrate status reset samples install dev-setup

help:
	@echo "KaizenMCP Database Migration Commands"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies with uv"
	@echo "  make migrate    - Apply pending migrations"
	@echo "  make status     - Show migration status"
	@echo "  make reset      - Reset database (interactive confirmation)"
	@echo "  make samples    - Load default sample data (001)"
	@echo "  make samples 002 - Load specific sample data"
	@echo "  make dev-setup  - Full dev setup (reset + migrate + samples)"
	@echo ""
	@echo "Environment variables:"
	@echo "  DATABASE_URL    - Override default database connection"
	@echo ""

install:
	uv sync

migrate:
	uv run python scripts/migrate.py

status:
	uv run python scripts/status.py

reset:
	uv run python scripts/reset.py

samples:
	uv run python scripts/load_samples.py $(filter-out $@,$(MAKECMDGOALS))

dev-setup:
	uv run python scripts/reset.py --confirm
	@$(MAKE) migrate
	@$(MAKE) samples
	@echo "✓ Development database ready"

# Prevent make from treating arguments as targets
%:
	@:
