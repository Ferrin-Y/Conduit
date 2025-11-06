from app.vectorstore.base import VectorStore

_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    # chromadb is a heavy optional dep, import it lazily so a broken/missing
    # build of it doesn't block app startup or unrelated tests
    global _store
    if _store is None:
        from app.vectorstore.chroma_store import ChromaVectorStore

        _store = ChromaVectorStore()
    return _store
