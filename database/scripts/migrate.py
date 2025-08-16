#!/usr/bin/env python3
"""
KaizenMCP Database Migration Script

Applies pending migrations to the database using Yoyo migrations.
"""
import os
import sys
from pathlib import Path

from yoyo import get_backend, read_migrations


def main():
    """Apply all pending migrations."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://kz_user:kz_pass@localhost:5452/kz_data')
    migrations_dir = Path(__file__).parent.parent / 'sql' / 'migrations'

    try:
        backend = get_backend(database_url)
        migrations = read_migrations(str(migrations_dir))

        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))

        print("✓ All migrations applied successfully")

    except Exception as e:
        print(f"✗ Migration failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
