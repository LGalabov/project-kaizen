"""Configuration management for Project Kaizen MCP server."""

import os
from dataclasses import dataclass
from typing import Literal

from project_kaizen.utils import parse_transport


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # Database settings
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://kz_user:kz_password@localhost:5453/kz_knowledge"
    )
    database_pool_min: int = int(os.getenv("DATABASE_POOL_MIN", "1"))
    database_pool_max: int = int(os.getenv("DATABASE_POOL_MAX", "2"))

    # Transport settings
    transport: Literal["stdio", "http"] = parse_transport(os.getenv("MCP_TRANSPORT"), "stdio")
    http_host: str = os.getenv("MCP_HTTP_HOST", "127.0.0.1")
    http_port: int = int(os.getenv("MCP_HTTP_PORT", "8000"))
    http_path: str = os.getenv("MCP_HTTP_PATH", "/mcp")


# Global config instance
config = Config()
