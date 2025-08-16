"""Configuration management for KaizenMCP server."""

import argparse
import os
from dataclasses import dataclass
from typing import Literal

from kaizen_mcp.utils import parse_transport

# Default configuration values
DEFAULT_DATABASE_URL = "postgresql://kz_user:kz_pass@localhost:5452/kz_data"
DEFAULT_POOL_MIN = 1
DEFAULT_POOL_MAX = 2
DEFAULT_TRANSPORT = "stdio"
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_PORT = 5453
DEFAULT_HTTP_PATH = "/mcp"


@dataclass
class Config:
    """Application configuration."""
    database_url: str
    database_pool_min: int
    database_pool_max: int
    transport: Literal["stdio", "http"]
    http_host: str
    http_port: int
    http_path: str

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Config":
        """Build config from CLI args > env vars > defaults."""
        return cls(
            database_url=args.db_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
            database_pool_min=(
                args.db_pool_min
                if args.db_pool_min is not None
                else int(os.getenv("DATABASE_POOL_MIN", str(DEFAULT_POOL_MIN)))
            ),
            database_pool_max=(
                args.db_pool_max
                if args.db_pool_max is not None
                else int(os.getenv("DATABASE_POOL_MAX", str(DEFAULT_POOL_MAX)))
            ),
            transport=parse_transport(
                args.transport or os.getenv("MCP_TRANSPORT"),
                DEFAULT_TRANSPORT
            ),
            http_host=args.http_host or os.getenv("MCP_HTTP_HOST", DEFAULT_HTTP_HOST),
            http_port=(
                args.http_port
                if args.http_port is not None
                else int(os.getenv("MCP_HTTP_PORT", str(DEFAULT_HTTP_PORT)))
            ),
            http_path=args.http_path or os.getenv("MCP_HTTP_PATH", DEFAULT_HTTP_PATH),
        )

    @classmethod
    def from_env(cls) -> "Config":
        """Build config from env vars and defaults only."""
        return cls(
            database_url=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
            database_pool_min=int(os.getenv("DATABASE_POOL_MIN", str(DEFAULT_POOL_MIN))),
            database_pool_max=int(os.getenv("DATABASE_POOL_MAX", str(DEFAULT_POOL_MAX))),
            transport=parse_transport(os.getenv("MCP_TRANSPORT"), DEFAULT_TRANSPORT),
            http_host=os.getenv("MCP_HTTP_HOST", DEFAULT_HTTP_HOST),
            http_port=int(os.getenv("MCP_HTTP_PORT", str(DEFAULT_HTTP_PORT))),
            http_path=os.getenv("MCP_HTTP_PATH", DEFAULT_HTTP_PATH),
        )


def create_parser() -> argparse.ArgumentParser:
    """Create a CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Project Kaizen MCP Server - Knowledge management for AI interactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (stdio transport)
  python -m project_kaizen
  
  # Run with HTTP transport
  python -m project_kaizen --transport http --http-port 8080
  
  # Custom database connection
  python -m project_kaizen --db-url postgresql://user:pass@host:5432/dbname
"""
    )

    # Database configuration
    db_group = parser.add_argument_group("database")
    db_group.add_argument("--db-url", help="PostgreSQL connection URL")
    db_group.add_argument("--db-pool-min", type=int, help="Minimum database pool size")
    db_group.add_argument("--db-pool-max", type=int, help="Maximum database pool size")

    # Transport configuration
    transport_group = parser.add_argument_group("transport")
    transport_group.add_argument("--transport", choices=["stdio", "http"], help="Transport type")
    transport_group.add_argument("--http-host", help="HTTP server host")
    transport_group.add_argument("--http-port", type=int, help="HTTP server port")
    transport_group.add_argument("--http-path", help="HTTP server path")

    return parser


# Global config instance - replaced at runtime
config = Config.from_env()
