from abc import ABC, abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def parse(self, filepath: str) -> str:
        """Extract text content from file for indexing."""
        ...
