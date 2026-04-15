from abc import ABC, abstractmethod
from typing import Any


class BaseIntegration(ABC):
    """Base class for all OSINT service integrations."""

    name: str = "base"
    description: str = ""
    rate_limit: int = 60  # requests per minute
    cache_ttl: int = 300  # seconds

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    @abstractmethod
    async def search(self, query: str, query_type: str = "domain") -> list[dict[str, Any]]:
        """Perform a search query and return results."""
        ...

    @abstractmethod
    async def check_health(self) -> dict[str, Any]:
        """Check service health and API key validity."""
        ...

    async def check_quota(self) -> dict[str, Any]:
        """Check remaining API quota/rate limits."""
        return await self.check_health()


class IntegrationRegistry:
    _registry: dict[str, type[BaseIntegration]] = {}

    @classmethod
    def register(cls, integration_cls: type[BaseIntegration]) -> type[BaseIntegration]:
        cls._registry[integration_cls.name] = integration_cls
        return integration_cls

    @classmethod
    def get(cls, name: str) -> type[BaseIntegration] | None:
        return cls._registry.get(name)

    @classmethod
    def list_all(cls) -> list[str]:
        return list(cls._registry.keys())
