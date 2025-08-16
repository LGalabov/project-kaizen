#!/usr/bin/env python3
"""
KaizenMCP Database Reset Script

Drops the entire database schema and re-applies all migrations.
WARNING: This will remove ALL data from the database.
"""
import os
import sys
from pathlib import Path

import psycopg2
from yoyo import get_backend, read_migrations


def drop_schema(database_url):
    """Drop all tables, functions, and types from the database."""
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DROP SCHEMA IF EXISTS public CASCADE;
                CREATE SCHEMA public;
                GRANT ALL ON SCHEMA public TO PUBLIC;
            """)
        conn.commit()
        print("✓ Database schema dropped and recreated")


def main():
    """Reset the database by dropping schema and re-applying migrations."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://kz_user:kz_pass@localhost:5452/kz_data')
    migrations_dir = Path(__file__).parent.parent / 'sql' / 'migrations'

    # Show consequences and ask for confirmation
    sys.stdout.write("⚠️  DATABASE RESET WARNING ⚠️\n")
    sys.stdout.write("=" * 50 + "\n")
    sys.stdout.write("This operation will:\n")
    sys.stdout.write("• Drop the entire database schema\n")
    sys.stdout.write("• Delete ALL user data permanently\n")
    sys.stdout.write("• Delete ALL knowledge entries\n")
    sys.stdout.write("• Delete ALL namespaces and scopes\n")
    sys.stdout.write("• Re-apply all migrations from scratch\n")
    sys.stdout.write("\n")
    sys.stdout.write("This action CANNOT be undone!\n")
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    # Skip confirmation if --confirm flag is present (for automation)
    if '--confirm' in sys.argv:
        print("Confirmation flag detected, proceeding...")
    else:
        confirmation = input("Type 'confirmed' to proceed with reset: ").strip()
        if confirmation != 'confirmed':
            print("Reset cancelled.")
            sys.exit(0)

    try:
        drop_schema(database_url)

        print("Re-applying migrations...")
        backend = get_backend(database_url)
        migrations = read_migrations(str(migrations_dir))

        pending = backend.to_apply(migrations)
        if pending:
            with backend.lock():
                backend.apply_migrations(pending)
            print(f"✓ Applied {len(pending)} migration(s)")
        else:
            print("No migrations to apply")

        print("✓ Database reset completed successfully")

    except Exception as e:
        print(f"✗ Reset failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
