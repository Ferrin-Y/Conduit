from sqlalchemy import select

from app.db.session import async_session
from app.ingestion.chunking import chunk_text
from app.models import Chunk, Document, DocumentStatus


async def process_document(document_id: int):
    async with async_session() as session:
        document = await session.get(Document, document_id)
        document.status = DocumentStatus.processing
        await session.commit()

        try:
            existing = await session.scalars(
                select(Chunk).where(Chunk.document_id == document_id)
            )
            for chunk in existing:
                await session.delete(chunk)

            pieces = chunk_text(document.content)
            for i, piece in enumerate(pieces):
                session.add(Chunk(document_id=document_id, index=i, text=piece))

            await session.commit()
        except Exception:
            await session.rollback()
            document.status = DocumentStatus.failed
            await session.commit()
            raise
