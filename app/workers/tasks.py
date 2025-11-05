from sqlalchemy import select

from app.db.session import async_session
from app.ingestion.chunking import chunk_text
from app.models import Chunk, Document, DocumentStatus
from app.vectorstore.base import VectorStore

_vector_store: VectorStore | None = None


def _get_vector_store() -> VectorStore:
    # imported lazily: chromadb is a heavy optional dep and we don't want
    # a broken/missing build of it to block app startup or unrelated tests
    global _vector_store
    if _vector_store is None:
        from app.vectorstore.chroma_store import ChromaVectorStore

        _vector_store = ChromaVectorStore()
    return _vector_store


async def process_document(document_id: int, vector_store: VectorStore | None = None):
    store = vector_store or _get_vector_store()
    async with async_session() as session:
        document = await session.get(Document, document_id)
        document.status = DocumentStatus.processing
        await session.commit()

        try:
            existing = list(
                await session.scalars(
                    select(Chunk).where(Chunk.document_id == document_id)
                )
            )
            if existing:
                store.delete([str(chunk.id) for chunk in existing])
            for chunk in existing:
                await session.delete(chunk)

            pieces = chunk_text(document.content)
            new_chunks = [
                Chunk(document_id=document_id, index=i, text=piece)
                for i, piece in enumerate(pieces)
            ]
            session.add_all(new_chunks)
            await session.flush()  # assign ids before we embed

            for chunk in new_chunks:
                chunk.vector_id = str(chunk.id)

            if new_chunks:
                # chroma generates the embeddings itself from the raw text
                store.add(
                    ids=[chunk.vector_id for chunk in new_chunks],
                    texts=[chunk.text for chunk in new_chunks],
                    metadatas=[
                        {"document_id": document_id, "chunk_index": chunk.index}
                        for chunk in new_chunks
                    ],
                )

            document.status = DocumentStatus.indexed
            await session.commit()
        except Exception:
            await session.rollback()
            document.status = DocumentStatus.failed
            await session.commit()
            raise
