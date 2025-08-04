"""Namespace service layer with business logic."""

from typing import Any

from ..types import NamespaceStyle, GLOBAL_NAMESPACE
from ..models.namespace import NamespaceData
from ..repositories.namespace import NamespaceRepository
from ..repositories.scope import ScopeRepository
import re


class NamespaceService:
    """Service for namespace business operations."""
    
    def __init__(self, namespace_repo: NamespaceRepository, scope_repo: ScopeRepository) -> None:
        self.namespace_repo = namespace_repo
        self.scope_repo = scope_repo
    
    def validate_namespace_name(self, name: str) -> None:
        """Validate namespace name follows kebab-case pattern."""
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            raise ValueError(f"Namespace name '{name}' must be kebab-case (lowercase letters, numbers, hyphens)")
    
    async def get_all_namespaces(
        self, 
        namespace: str | None = None, 
        style: NamespaceStyle = NamespaceStyle.SHORT
    ) -> dict[str, NamespaceData]:
        """Get all namespaces with optional filtering and style."""
        return await self.namespace_repo.list_all(namespace, style)
    
    async def create_namespace(self, name: str, description: str) -> dict[str, Any]:
        """Create new namespace with validation and automatic default scope."""
        self.validate_namespace_name(name)
        
        if name == GLOBAL_NAMESPACE:
            raise ValueError(f"Cannot create namespace '{GLOBAL_NAMESPACE}' - reserved name")
        
        return await self.namespace_repo.create(name, description)
    
    async def update_namespace(
        self, 
        name: str, 
        new_name: str | None = None, 
        description: str | None = None
    ) -> dict[str, Any]:
        """Update namespace with validation and global protection."""
        if name == GLOBAL_NAMESPACE:
            raise ValueError(f"Cannot modify global namespace '{GLOBAL_NAMESPACE}'")
        
        if new_name:
            self.validate_namespace_name(new_name)
            if new_name == GLOBAL_NAMESPACE:
                raise ValueError(f"Cannot rename to '{GLOBAL_NAMESPACE}' - reserved name")
        
        return await self.namespace_repo.update(name, new_name, description)
    
    async def delete_namespace(self, name: str) -> dict[str, Any]:
        """Delete namespace with global protection."""
        if name == GLOBAL_NAMESPACE:
            raise ValueError(f"Cannot delete global namespace '{GLOBAL_NAMESPACE}'")
        
        return await self.namespace_repo.delete(name)