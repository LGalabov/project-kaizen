"""Exception hierarchy for Project Kaizen MCP Server."""

from typing import Any


class ProjectKaizenError(Exception):
    """Base exception for all Project Kaizen errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class ConfigurationError(ProjectKaizenError):
    """Configuration and settings related errors."""

    pass


class DatabaseError(ProjectKaizenError):
    """Database connection and query errors."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Database connection establishment errors."""

    pass


class DatabaseQueryError(DatabaseError):
    """Database query execution errors."""

    pass


class ValidationError(ProjectKaizenError):
    """Input validation and Pydantic model errors."""

    pass


class MCPProtocolError(ProjectKaizenError):
    """MCP protocol compliance and communication errors."""

    pass


class NamespaceError(ProjectKaizenError):
    """Namespace management errors."""

    pass


class NamespaceNotFoundError(NamespaceError):
    """Requested namespace does not exist."""

    pass


class NamespaceAlreadyExistsError(NamespaceError):
    """Namespace with given name already exists."""

    pass


class ScopeError(ProjectKaizenError):
    """Scope management errors."""

    pass


class ScopeNotFoundError(ScopeError):
    """Requested scope does not exist."""

    pass


class ScopeAlreadyExistsError(ScopeError):
    """Scope with given name already exists."""

    pass


class DefaultScopeDeletionError(ScopeError):
    """Attempted to delete protected default scope."""

    pass


class KnowledgeError(ProjectKaizenError):
    """Knowledge management errors."""

    pass


class KnowledgeNotFoundError(KnowledgeError):
    """Requested knowledge entry does not exist."""

    pass


class ConflictResolutionError(KnowledgeError):
    """Knowledge conflict resolution errors."""

    pass
