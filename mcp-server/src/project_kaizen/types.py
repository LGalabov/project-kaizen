"""Common types, enums, and constants for Project Kaizen MCP Server."""

from enum import Enum
from typing import Literal


class TaskSize(str, Enum):
    """Task complexity levels for knowledge filtering."""

    XS = "XS"  # Quick fixes
    S = "S"   # Small features
    M = "M"   # Medium projects
    L = "L"   # Large implementations
    XL = "XL" # Architectural changes


class NamespaceStyle(str, Enum):
    """MCP query detail levels."""

    SHORT = "short"    # Names and descriptions only
    LONG = "long"      # Include scopes
    DETAILS = "details" # Include scope parents


# Common type aliases
ScopeName = str     # Format: "namespace:scope"
NamespaceName = str # Globally unique identifier
KnowledgeID = str   # Entry ID (e.g., "K7H9M2PQX8")

# Validation literals
TaskSizeLiteral = Literal["XS", "S", "M", "L", "XL"]
NamespaceStyleLiteral = Literal["short", "long", "details"]

# System constants
DEFAULT_SCOPE_NAME = "default"
GLOBAL_NAMESPACE = "global"
GLOBAL_DEFAULT_SCOPE = "global:default"

# Database limits
MIN_DB_CONNECTIONS = 1
MAX_DB_CONNECTIONS = 20
DEFAULT_DB_CONNECTIONS = 10
