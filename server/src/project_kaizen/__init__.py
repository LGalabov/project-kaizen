"""
Project Kaizen MCP Server.

A Model Context Protocol (MCP) server for persistent knowledge management,
enabling AI assistants to maintain context across conversations.
"""

__version__ = "1.0.0"

# Public API exports
from project_kaizen.config import Config, config

__all__ = [
    "Config",
    "config",
    "__version__",
]
