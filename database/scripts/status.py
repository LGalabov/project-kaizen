#!/usr/bin/env python3
"""
KaizenMCP Database Migration Status Script

Shows current migration status and pending migrations.
"""
import os
import sys
from pathlib import Path

from yoyo import get_backend, read_migrations


def main():
    """Show migration status."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://kz_user:kz_pass@localhost:5452/kz_data')
    migrations_dir = Path(__file__).parent.parent / 'sql' / 'migrations'

    try:
        backend = get_backend(database_url)
        migrations = read_migrations(str(migrations_dir))

        # Get applied and pending migrations
        applied = backend.to_rollback(migrations)
        pending = backend.to_apply(migrations)

        print("Migration Status")
        print("=" * 50)
        print(f"Database: {database_url}")
        print(f"Migrations directory: {migrations_dir}")
        print()

        if applied:
            print(f"Applied migrations ({len(applied)}):")
            for migration in applied:
                print(f"  ✓ {migration.id}")
        else:
            print("No applied migrations")

        print()

        if pending:
            print(f"Pending migrations ({len(pending)}):")
            for migration in pending:
                print(f"  • {migration.id}")
        else:
            print("No pending migrations")

    except Exception as e:
        print(f"✗ Status check failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
