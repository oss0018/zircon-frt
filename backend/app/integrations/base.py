from abc import ABC, abstractmethod
from typing import Any


class BaseIntegration(ABC):
    """Base class for all OSINT service integrations."""

    name: str = "base"
    description: str = ""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    @abstractmethod
    async def search(self, query: str) -> list[dict[str, Any]]:
        """Perform a search query and return results."""
        ...

    @abstractmethod
    async def check_quota(self) -> dict[str, Any]:
        """Check remaining API quota/rate limits."""
        ...


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
