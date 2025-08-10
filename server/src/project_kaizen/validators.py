"""
Validation functions for Project Kaizen MCP Server.

This module provides validation functions for all input parameters
used in the MCP server.
"""

import re

from .utils import parse_canonical_scope_name

# Validation constants - easy to modify limits and patterns
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 64

MIN_KEYWORD_LENGTH = 2
MAX_KEYWORD_LENGTH = 32
MAX_CONTEXT_KEYWORDS = 20
MAX_QUERIES_PER_SEARCH = 15
MAX_KEYWORDS_PER_QUERY = 10

# Regular expressions for validation
NAMESPACE_PATTERN = re.compile(r"^[a-z0-9\-]+$")
SCOPE_NAME_PATTERN = re.compile(r"^[a-z0-9\-]+$")
KEYWORD_PATTERN = re.compile(rf"^[a-z0-9\-]{{{MIN_KEYWORD_LENGTH},{MAX_KEYWORD_LENGTH}}}$")
CONTEXT_PATTERN = re.compile(
    rf"^[a-z0-9\-]{{{MIN_KEYWORD_LENGTH},{MAX_KEYWORD_LENGTH}}}"
    rf"( [a-z0-9\-]{{{MIN_KEYWORD_LENGTH},{MAX_KEYWORD_LENGTH}}}){{{0},{MAX_CONTEXT_KEYWORDS-1}}}$"
)
QUERY_PATTERN = re.compile(
    rf"^[a-z0-9\-]{{{MIN_KEYWORD_LENGTH},{MAX_KEYWORD_LENGTH}}}"
    rf"( [a-z0-9\-]{{{MIN_KEYWORD_LENGTH},{MAX_KEYWORD_LENGTH}}}){{{0},{MAX_KEYWORDS_PER_QUERY-1}}}$"
)

# Valid enum values
VALID_TASK_SIZES = {"XS", "S", "M", "L", "XL"}


def validate_namespace_name(namespace_name: str | None) -> None:
    """
    Validates the namespace name format (2-64 chars, lowercase/digits/-).

    Raises:
        ValueError: if namespace_name contains invalid characters or a wrong length
    """
    if namespace_name is None or namespace_name == "":
        raise ValueError("Namespace name cannot be empty")
    
    if not namespace_name.strip():
        raise ValueError("Namespace name cannot be just whitespace")

    if len(namespace_name) < MIN_NAME_LENGTH or len(namespace_name) > MAX_NAME_LENGTH:
        raise ValueError(f"Namespace name must be {MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} characters")

    if not NAMESPACE_PATTERN.match(namespace_name):
        raise ValueError("Namespace name must contain only lowercase letters, numbers, and hyphens")


def validate_scope_name(scope_name: str | None) -> None:
    """
    Validates the scope name format (2-64 chars, lowercase/digits/-).

    Raises:
        ValueError: if scope_name contains invalid characters or a wrong length
    """
    if scope_name is None or scope_name == "":
        raise ValueError("Scope name cannot be empty")
    
    if not scope_name.strip():
        raise ValueError("Scope name cannot be just whitespace")

    if len(scope_name) < MIN_NAME_LENGTH or len(scope_name) > MAX_NAME_LENGTH:
        raise ValueError(f"Scope name must be {MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} characters")

    if not SCOPE_NAME_PATTERN.match(scope_name):
        raise ValueError("Scope name must contain only lowercase letters, numbers, and hyphens")


def validate_canonical_scope_name(canonical_scope_name: str | None) -> None:
    """
    Validates canonical scope name format 'namespace:scope'.
    Delegates validation of individual parts to namespace and scope validators.

    Raises:
        ValueError: if the format is invalid, or parts don't meet requirements
    """
    if canonical_scope_name is None or canonical_scope_name == "":
        raise ValueError("Canonical scope name cannot be empty")
    
    if not canonical_scope_name.strip():
        raise ValueError("Canonical scope name cannot be just whitespace")

    namespace_name, scope_name = parse_canonical_scope_name(canonical_scope_name.strip())

    validate_namespace_name(namespace_name)
    validate_scope_name(scope_name)


def validate_description(description: str | None) -> None:
    """
    Validates description is 2-64 chars and not just whitespace.

    Raises:
        ValueError: if the description is just whitespace or wrong length
    """
    if description is None or description == "":
        raise ValueError("Description cannot be empty")
    
    if not description.strip():
        raise ValueError("Description cannot be just whitespace")

    if len(description) < MIN_NAME_LENGTH or len(description) > MAX_NAME_LENGTH:
        raise ValueError(f"Description must be {MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} characters")


def validate_content(content: str | None) -> None:
    """
    Validates knowledge content is not empty or just whitespace.

    Raises:
        ValueError: if content is empty or only whitespace
    """
    if content is None or content == "":
        raise ValueError("Knowledge content cannot be empty")
    
    if not content.strip():
        raise ValueError("Knowledge content cannot be just whitespace")


def validate_context(context: str | None) -> None:
    """
    Validates the knowledge context format: 1-20 space-separated keywords.
    Each keyword must be 2-32 characters, lowercase letters, digits, and hyphens only.

    Raises:
        ValueError: if context is empty, malformed, or has invalid keyword count/format
    """
    if context is None or context == "":
        raise ValueError("Knowledge context cannot be empty")
    
    if not context.strip():
        raise ValueError("Knowledge context cannot be just whitespace")
    
    if not CONTEXT_PATTERN.match(context.strip()):
        raise ValueError(
            f"Knowledge context must be 1-{MAX_CONTEXT_KEYWORDS} space-separated keywords, "
            f"each {MIN_KEYWORD_LENGTH}-{MAX_KEYWORD_LENGTH} chars (lowercase letters/digits/hyphens only)"
        )


def validate_query_terms(queries: list[str] | None) -> None:
    """
    Validates search query terms: 1-15 queries, each with 1-10 space-separated keywords.
    Each keyword must be 2-32 characters, lowercase letters, digits, and hyphens only.

    Raises:
        ValueError: if the query list is empty, too long, or contains malformed queries
    """
    if queries is None or len(queries) == 0:
        raise ValueError("Query terms cannot be empty")
    
    if len(queries) > MAX_QUERIES_PER_SEARCH:
        raise ValueError(f"Maximum {MAX_QUERIES_PER_SEARCH} search queries allowed")
    
    for i, query in enumerate(queries):
        if query is None or query == "":
            raise ValueError(f"Query {i+1} cannot be empty")
        
        if not query.strip():
            raise ValueError(f"Query {i+1} cannot be just whitespace")
        
        if not QUERY_PATTERN.match(query.strip()):
            raise ValueError(
                f"Query {i+1} must be 1-{MAX_KEYWORDS_PER_QUERY} space-separated keywords, "
                f"each {MIN_KEYWORD_LENGTH}-{MAX_KEYWORD_LENGTH} chars (lowercase letters/digits/hyphens only)"
            )


def validate_task_size(task_size: str | None) -> None:
    """
    Validates task size is one of: 'XS', 'S', 'M', 'L', 'XL'.
    Accepts None for optional fields.

    Raises:
        ValueError: if task_size is not a valid option
    """
    if task_size is None:
        return
    
    if task_size == "":
        raise ValueError("Task size cannot be empty string")
    
    if not task_size.strip():
        raise ValueError("Task size cannot be just whitespace")

    if task_size not in VALID_TASK_SIZES:
        raise ValueError(f"Task size must be one of: {', '.join(sorted(VALID_TASK_SIZES))}")
