"""Knowledge service layer with business logic."""

from ..repositories.knowledge import KnowledgeRepository
from ..repositories.scope import ScopeRepository
from ..utils.logging import log_database_operation


class KnowledgeService:
    """Service for knowledge business operations."""

    def __init__(
        self, knowledge_repo: KnowledgeRepository, scope_repo: ScopeRepository
    ) -> None:
        self.knowledge_repo = knowledge_repo
        self.scope_repo = scope_repo

    async def create_knowledge_entry(
        self, scope: str, content: str, context: str
    ) -> str:
        """Create knowledge entry with scope validation."""
        namespace_name, scope_name = scope.split(":", 1)

        # Validate scope exists
        scope_info = await self.scope_repo.get_by_name(namespace_name, scope_name)
        if not scope_info:
            raise ValueError(f"Scope '{scope}' not found")

        scope_id = scope_info["id"]

        # Create knowledge entry
        return await self.knowledge_repo.create(scope_id, content, context)

    async def update_knowledge_entry(
        self,
        entry_id: str,
        content: str | None = None,
        context: str | None = None,
        scope: str | None = None,
    ) -> str:
        """Update knowledge entry with optional scope change."""
        # Get current knowledge entry
        current_entry = await self.knowledge_repo.get_by_id(entry_id)
        if not current_entry:
            raise ValueError(f"Knowledge entry '{entry_id}' not found")

        current_scope: str = current_entry["scope_name"]
        final_scope_id: int = current_entry["scope_id"]
        final_scope: str = current_scope

        # Handle scope change if requested
        if scope:
            namespace_name, scope_name = scope.split(":", 1)

            # Get new scope info
            scope_info = await self.scope_repo.get_by_name(namespace_name, scope_name)
            if not scope_info:
                raise ValueError(f"Target scope '{scope}' not found")

            final_scope_id = scope_info["id"]
            final_scope = scope

        # Update knowledge entry
        await self.knowledge_repo.update(
            entry_id, content, context, final_scope_id if scope else None
        )

        return final_scope

    async def delete_knowledge_entry(self, entry_id: str) -> str:
        """Delete knowledge entry with validation."""
        # Verify entry exists before deletion
        entry = await self.knowledge_repo.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Knowledge entry '{entry_id}' not found")

        await self.knowledge_repo.delete(entry_id)
        return entry_id

    async def resolve_knowledge_conflicts(
        self, active_id: str, suppressed_ids: list[str]
    ) -> tuple[str, list[str]]:
        """Mark knowledge entries for conflict resolution."""
        # Verify active knowledge exists
        active_entry = await self.knowledge_repo.get_by_id(active_id)
        if not active_entry:
            raise ValueError(f"Active knowledge entry '{active_id}' not found")

        # Verify all suppressed knowledge entries exist
        for suppressed_id in suppressed_ids:
            suppressed_entry = await self.knowledge_repo.get_by_id(suppressed_id)
            if not suppressed_entry:
                raise ValueError(
                    f"Suppressed knowledge entry '{suppressed_id}' not found"
                )

        # Mark suppressed entries
        for suppressed_id in suppressed_ids:
            await self.knowledge_repo.mark_suppressed(suppressed_id, active_id)

        log_database_operation(
            "UPDATE",
            query="suppress_knowledge_conflicts",
            params=[active_id, len(suppressed_ids)],
        )

        return active_id, suppressed_ids

    async def get_task_context_knowledge(
        self, queries: list[str], scope: str, task_size: str | None = None
    ) -> dict[str, dict[str, str]]:
        """Get relevant knowledge for complex tasks using scope hierarchy."""
        namespace_name, scope_name = scope.split(":", 1)

        # Validate starting scope exists
        scope_info = await self.scope_repo.get_by_name(namespace_name, scope_name)
        if not scope_info:
            raise ValueError(f"Scope '{scope}' not found")

        # This is a complex query that needs to be implemented in the repository
        # For now, we'll use a simplified approach
        scope_id = scope_info["id"]

        # Search knowledge entries
        knowledge_results = await self.knowledge_repo.search_by_queries(
            queries, [scope_id], task_size
        )

        # Organize results by scope hierarchy
        results: dict[str, dict[str, str]] = {}

        for row in knowledge_results:
            scope_name = row["scope_name"]
            knowledge_id = str(row["id"])
            content = row["content"]

            if scope_name not in results:
                results[scope_name] = {}

            results[scope_name][knowledge_id] = content

        return results
