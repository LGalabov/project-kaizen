"""Scope service layer with business logic."""

from typing import Any

from ..types import DEFAULT_SCOPE_NAME
from ..repositories.namespace import NamespaceRepository
from ..repositories.scope import ScopeRepository
from ..utils.logging import log_database_operation


class ScopeService:
    """Service for scope business operations."""
    
    def __init__(self, namespace_repo: NamespaceRepository, scope_repo: ScopeRepository) -> None:
        self.namespace_repo = namespace_repo
        self.scope_repo = scope_repo
    
    async def create_scope(
        self, 
        scope: str, 
        description: str, 
        parents: list[str] | None = None
    ) -> dict[str, Any]:
        """Create new scope with automatic default parent inheritance."""
        namespace_name, scope_name = scope.split(":", 1)
        
        # Get namespace info
        namespace_info = await self.namespace_repo.get_by_name(namespace_name)
        if not namespace_info:
            raise ValueError(f"Namespace '{namespace_name}' not found")
        
        namespace_id: int = namespace_info["id"]
        
        # Auto-add default parent if not specified
        all_parents = list(parents or [])
        default_parent = f"{namespace_name}:{DEFAULT_SCOPE_NAME}"
        if default_parent not in all_parents:
            all_parents.append(default_parent)
        
        # Get parent IDs
        parent_ids: list[int] = []
        for parent_scope in all_parents:
            parent_namespace, parent_name = parent_scope.split(":", 1)
            parent_info = await self.scope_repo.get_by_name(parent_namespace, parent_name)
            
            if not parent_info:
                raise ValueError(f"Parent scope '{parent_scope}' not found")
            
            parent_ids.append(parent_info["id"])
        
        # Create scope
        log_database_operation("INSERT", query="create_scope", params=[namespace_id, scope_name, description])
        await self.scope_repo.create(namespace_id, scope_name, description, parent_ids)
        
        return {
            "scope": scope,
            "description": description,
            "parents": all_parents,
        }
    
    async def update_scope(
        self,
        scope: str,
        new_scope: str | None = None,
        description: str | None = None,
        parents: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update scope with validation and automatic reference updating."""
        current_namespace, current_scope_name = scope.split(":", 1)
        
        # Get current scope info
        scope_info = await self.scope_repo.get_by_name(current_namespace, current_scope_name)
        if not scope_info:
            raise ValueError(f"Scope '{scope}' not found")
        
        scope_id = scope_info["id"]
        current_description = scope_info["description"]
        
        # Handle scope name update if requested
        final_scope_name = scope
        if new_scope:
            new_namespace, new_scope_name = new_scope.split(":", 1)
            
            # Scope can only be renamed within the same namespace
            if new_namespace != current_namespace:
                raise ValueError("Cannot move scope to different namespace")
            
            await self.scope_repo.update_name(scope_id, new_scope_name)
            final_scope_name = new_scope
        
        # Handle description update if requested
        final_description = current_description
        if description:
            await self.scope_repo.update_description(scope_id, description)
            final_description = description
        
        # Handle parent relationships update if requested
        final_parents: list[str] = []
        if parents is not None:
            # Clear existing parents
            await self.scope_repo.clear_parents(scope_id)
            
            # Ensure default parent is preserved
            new_parents = list(parents)
            default_parent = f"{current_namespace}:{DEFAULT_SCOPE_NAME}"
            if default_parent not in new_parents:
                new_parents.append(default_parent)
            
            # Add new parent relationships
            for parent_scope in new_parents:
                parent_namespace, parent_name = parent_scope.split(":", 1)
                parent_info = await self.scope_repo.get_by_name(parent_namespace, parent_name)
                
                if not parent_info:
                    raise ValueError(f"Parent scope '{parent_scope}' not found")
                
                await self.scope_repo.add_parent(scope_id, parent_info["id"])
            
            final_parents = new_parents
        else:
            # Get current parents
            final_parents = await self.scope_repo.get_parents(scope_id)
        
        log_database_operation("UPDATE", query="update_scope_complete", params=[scope_id])
        
        return {
            "scope": final_scope_name,
            "description": final_description,
            "parents": final_parents,
        }
    
    async def delete_scope(self, scope: str) -> dict[str, Any]:
        """Delete scope and return knowledge count."""
        namespace_name, scope_name = scope.split(":", 1)
        
        # Get scope info
        scope_info = await self.scope_repo.get_by_name(namespace_name, scope_name)
        if not scope_info:
            raise ValueError(f"Scope '{scope}' not found")
        
        scope_id = scope_info["id"]
        
        # Delete scope and get knowledge count
        knowledge_count = await self.scope_repo.delete(scope_id)
        
        return {"scope": scope, "knowledge_deleted": knowledge_count}