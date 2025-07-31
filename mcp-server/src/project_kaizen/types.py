"""Common types, enums, and constants for Project Kaizen MCP Server."""

from enum import Enum
from typing import Literal, TypeAlias


# Task size filtering for knowledge complexity
class TaskSize(str, Enum):
    """Task complexity levels for knowledge filtering."""
    XS = "XS"  # Quick fixes
    S = "S"    # Small features
    M = "M"    # Medium projects
    L = "L"    # Large implementations
    XL = "XL"  # Architectural changes


# MCP Protocol Style Options
class NamespaceStyle(str, Enum):
    """Namespace query detail levels."""
    SHORT = "short"    # Names and descriptions only
    LONG = "long"      # Include scopes
    DETAILS = "details"  # Include scope parents


# Type aliases for common identifiers
ScopeName: TypeAlias = str  # Format: "namespace:scope" or "global:default"
NamespaceName: TypeAlias = str  # Globally unique namespace identifier
KnowledgeID: TypeAlias = str  # Knowledge entry identifier (e.g., "K7H9M2PQX8")


# Literal types for validation
TaskSizeLiteral = Literal["XS", "S", "M", "L", "XL"]
NamespaceStyleLiteral = Literal["short", "long", "details"]


# Constants
DEFAULT_SCOPE_NAME = "default"
GLOBAL_NAMESPACE = "global"
GLOBAL_DEFAULT_SCOPE = "global:default"

# Database connection limits
MIN_DB_CONNECTIONS = 1
MAX_DB_CONNECTIONS = 20
DEFAULT_DB_CONNECTIONS = 10
