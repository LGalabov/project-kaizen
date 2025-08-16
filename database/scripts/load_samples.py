#!/usr/bin/env python3
"""
KaizenMCP Sample Data Loader

Loads sample data files into the database for development and testing.
"""
import os
import sys
import glob
import psycopg2
from pathlib import Path


def execute_sql_file(database_url, sql_file_path):
    """Execute SQL file against the database."""
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            with open(sql_file_path, 'r') as f:
                sql_content = f.read()
            
            cur.execute(sql_content)
        conn.commit()
        print(f"✓ Executed {sql_file_path}")


def main():
    """Load sample data file."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://kz_user:kz_pass@localhost:5452/kz_data')
    
    # Get the sample number from args or default to 001
    sample_num = sys.argv[1] if len(sys.argv) > 1 else '001'
    
    # Find a matching sample file
    sample_data_dir = Path(__file__).parent.parent / 'sql' / 'sample-data'
    pattern = str(sample_data_dir / f'{sample_num}_*.sql')
    sample_files = glob.glob(pattern)
    
    if not sample_files:
        print(f"✗ No sample file found for number {sample_num}")
        print(f"Looking for pattern: {pattern}")
        sys.exit(1)
    
    if len(sample_files) > 1:
        print(f"✗ Multiple sample files found for number {sample_num}: {sample_files}")
        sys.exit(1)
    
    sample_file = sample_files[0]
    
    try:
        execute_sql_file(database_url, sample_file)
        print(f"✓ Sample data {sample_num} loaded successfully")
        
    except Exception as e:
        print(f"✗ Failed to load sample data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
