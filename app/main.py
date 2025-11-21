from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.repository import create_document
from app.db.repository import get_document as fetch_document
from app.db.session import get_session
from app.ingestion.fetch import close_http_client, fetch_url_text
from app.schemas import DocumentCreate, DocumentRead, QueryRequest, QueryResponse, QueryResult
from app.vectorstore import get_vector_store
from app.workers.queue import job_queue
from app.workers.tasks import process_document


@asynccontextmanager
async def lifespan(app: FastAPI):
    await job_queue.start()
    yield
    await job_queue.stop()
    await close_http_client()


app = FastAPI(title="Conduit", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "db": settings.database_url}


@app.post("/documents", response_model=DocumentRead)
async def ingest_document(payload: DocumentCreate, session: AsyncSession = Depends(get_session)):
    content = payload.content
    if content is None:
        content = await fetch_url_text(payload.source_url)

    document = await create_document(session, payload.title, content)

    await job_queue.enqueue(lambda: process_document(document.id))

    return document


@app.get("/documents/{doc_id}", response_model=DocumentRead)
async def get_document(doc_id: int, session: AsyncSession = Depends(get_session)):
    document = await fetch_document(session, doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    return document


@app.post("/query", response_model=QueryResponse)
def semantic_query(payload: QueryRequest):
    store = get_vector_store()
    results = store.query(payload.query, top_k=payload.top_k)
    return QueryResponse(
        results=[
            QueryResult(
                text=r.text,
                distance=r.distance,
                document_id=r.metadata.get("document_id"),
            )
            for r in results
        ]
    )
