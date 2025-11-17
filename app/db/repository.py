from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chunk, Document, DocumentStatus


async def create_document(session: AsyncSession, title: str, content: str) -> Document:
    document = Document(title=title, content=content)
    session.add(document)
    await session.commit()
    return document


async def get_document(session: AsyncSession, document_id: int) -> Document | None:
    return await session.get(Document, document_id)


async def set_document_status(
    session: AsyncSession, document: Document, status: DocumentStatus
) -> None:
    document.status = status
    await session.commit()


async def replace_chunks(session: AsyncSession, document_id: int, texts: list[str]) -> list[Chunk]:
    existing = await session.scalars(select(Chunk).where(Chunk.document_id == document_id))
    for chunk in existing:
        await session.delete(chunk)

    new_chunks = [
        Chunk(document_id=document_id, index=i, text=text) for i, text in enumerate(texts)
    ]
    session.add_all(new_chunks)
    await session.flush()
    return new_chunks
