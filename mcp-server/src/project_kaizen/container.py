"""Dependency injection container for clean component wiring."""

from .infrastructure.database import DatabasePool, get_database_pool
from .repositories.namespace import NamespaceRepository
from .repositories.scope import ScopeRepository
from .repositories.knowledge import KnowledgeRepository
from .services.namespace import NamespaceService
from .services.scope import ScopeService
from .services.knowledge import KnowledgeService


class Container:
    """Dependency injection container managing component lifecycle."""

    def __init__(self) -> None:
        self._database_pool: DatabasePool | None = None
        self._namespace_repository: NamespaceRepository | None = None
        self._scope_repository: ScopeRepository | None = None
        self._knowledge_repository: KnowledgeRepository | None = None
        self._namespace_service: NamespaceService | None = None
        self._scope_service: ScopeService | None = None
        self._knowledge_service: KnowledgeService | None = None

    def database_pool(self) -> DatabasePool:
        """Get database pool singleton."""
        if self._database_pool is None:
            self._database_pool = get_database_pool()
        return self._database_pool

    def namespace_repository(self) -> NamespaceRepository:
        """Get namespace repository singleton."""
        if self._namespace_repository is None:
            self._namespace_repository = NamespaceRepository()
        return self._namespace_repository

    def scope_repository(self) -> ScopeRepository:
        """Get scope repository singleton."""
        if self._scope_repository is None:
            self._scope_repository = ScopeRepository()
        return self._scope_repository

    def knowledge_repository(self) -> KnowledgeRepository:
        """Get knowledge repository singleton."""
        if self._knowledge_repository is None:
            self._knowledge_repository = KnowledgeRepository()
        return self._knowledge_repository

    def namespace_service(self) -> NamespaceService:
        """Get namespace service with injected dependencies."""
        if self._namespace_service is None:
            self._namespace_service = NamespaceService(
                namespace_repo=self.namespace_repository(),
                scope_repo=self.scope_repository(),
            )
        return self._namespace_service

    def scope_service(self) -> ScopeService:
        """Get scope service with injected dependencies."""
        if self._scope_service is None:
            self._scope_service = ScopeService(
                namespace_repo=self.namespace_repository(),
                scope_repo=self.scope_repository(),
            )
        return self._scope_service

    def knowledge_service(self) -> KnowledgeService:
        """Get knowledge service with injected dependencies."""
        if self._knowledge_service is None:
            self._knowledge_service = KnowledgeService(
                knowledge_repo=self.knowledge_repository(),
                scope_repo=self.scope_repository(),
            )
        return self._knowledge_service

    async def initialize_database(
        self, db_url: str, db_user: str, db_password: str, db_name: str
    ) -> None:
        """Initialize database connection pool."""
        await self.database_pool().initialize(db_url, db_user, db_password, db_name)

    async def close_resources(self) -> None:
        """Clean up resources on shutdown."""
        if self._database_pool:
            await self._database_pool.close()


# Global container instance
_container: Container | None = None


def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def reset_container() -> None:
    """Reset container for testing purposes."""
    global _container
    _container = None
