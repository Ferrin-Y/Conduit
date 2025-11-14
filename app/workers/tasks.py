from sqlalchemy import select

from app.db.repository import get_document, replace_chunks, set_document_status
from app.db.session import async_session
from app.ingestion.chunking import chunk_text
from app.models import Chunk, DocumentStatus
from app.vectorstore import get_vector_store
from app.vectorstore.base import VectorStore


async def process_document(document_id: int, vector_store: VectorStore | None = None):
    store = vector_store or get_vector_store()
    async with async_session() as session:
        document = await get_document(session, document_id)
        await set_document_status(session, document, DocumentStatus.processing)

        try:
            old_chunk_ids = list(
                await session.scalars(
                    select(Chunk.id).where(Chunk.document_id == document_id)
                )
            )
            if old_chunk_ids:
                store.delete([str(chunk_id) for chunk_id in old_chunk_ids])

            pieces = chunk_text(document.content)
            new_chunks = await replace_chunks(session, document_id, pieces)

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

            await set_document_status(session, document, DocumentStatus.indexed)
        except Exception:
            await session.rollback()
            await set_document_status(session, document, DocumentStatus.failed)
            raise
