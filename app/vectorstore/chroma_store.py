import chromadb

from app.config import settings
from app.vectorstore.base import SearchResult, VectorStore

COLLECTION_NAME = "conduit_chunks"


class ChromaVectorStore(VectorStore):
    def __init__(self):
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(COLLECTION_NAME)

    def add(self, ids: list[str], texts: list[str], metadatas: list[dict]) -> None:
        self._collection.add(ids=ids, documents=texts, metadatas=metadatas)

    def query(self, text: str, top_k: int = 5) -> list[SearchResult]:
        results = self._collection.query(query_texts=[text], n_results=top_k)
        out = []
        for vector_id, doc, distance, metadata in zip(
            results["ids"][0],
            results["documents"][0],
            results["distances"][0],
            results["metadatas"][0],
        ):
            out.append(
                SearchResult(
                    vector_id=vector_id, text=doc, distance=distance, metadata=metadata
                )
            )
        return out

    def delete(self, ids: list[str]) -> None:
        self._collection.delete(ids=ids)
