from app.vectorstore.base import SearchResult, VectorStore


class FakeVectorStore(VectorStore):
    def __init__(self):
        self.records: dict[str, dict] = {}

    def add(self, ids, texts, metadatas):
        for vector_id, text, metadata in zip(ids, texts, metadatas, strict=True):
            self.records[vector_id] = {"text": text, "metadata": metadata}

    def query(self, text: str, top_k: int = 5) -> list[SearchResult]:
        matches = [
            SearchResult(vector_id=vid, text=r["text"], distance=0.0, metadata=r["metadata"])
            for vid, r in self.records.items()
            if text.lower() in r["text"].lower()
        ]
        return matches[:top_k]

    def delete(self, ids):
        for vector_id in ids:
            self.records.pop(vector_id, None)
