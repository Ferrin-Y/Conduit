from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    vector_id: str
    text: str
    distance: float
    metadata: dict


class VectorStore(ABC):
    @abstractmethod
    def add(self, ids: list[str], texts: list[str], metadatas: list[dict]) -> None: ...

    @abstractmethod
    def query(self, text: str, top_k: int = 5) -> list[SearchResult]: ...

    @abstractmethod
    def delete(self, ids: list[str]) -> None: ...
