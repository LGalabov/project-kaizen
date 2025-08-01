from . import server
import asyncio
import argparse
import os
from typing import Literal, cast


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description='Project Kaizen MCP Server')
    parser.add_argument('--db-url', default=None, help='PostgreSQL connection URL')
    parser.add_argument('--db-user', default=None, help='PostgreSQL username')
    parser.add_argument('--db-password', default=None, help='PostgreSQL password')
    parser.add_argument('--db-name', default=None, help='PostgreSQL database name')
    parser.add_argument("--transport", default=None, help="Transport type (stdio, http)")
    parser.add_argument("--server-host", default=None, help="HTTP host (default: 127.0.0.1)")
    parser.add_argument("--server-port", type=int, default=None, help="HTTP port (default: 8000)")
    parser.add_argument("--server-path", default=None, help="HTTP path (default: /mcp/)")
    
    args = parser.parse_args()
    
    asyncio.run(server.main(
        args.db_url or os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/project_kaizen"),
        args.db_user or os.getenv("POSTGRES_USER", "postgres"),
        args.db_password or os.getenv("POSTGRES_PASSWORD", "postgres"),
        args.db_name or os.getenv("POSTGRES_DB", "project_kaizen"),
        cast(Literal["stdio", "http"], args.transport or os.getenv("KAIZEN_TRANSPORT", "stdio")),
        args.server_host or os.getenv("KAIZEN_SERVER_HOST", "127.0.0.1"),
        args.server_port or int(os.getenv("KAIZEN_SERVER_PORT", "8000")),
        args.server_path or os.getenv("KAIZEN_SERVER_PATH", "/mcp/"),
    ))


# Optionally expose other important items at package level
__all__ = ["main", "server"]
