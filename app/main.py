from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.models import Document
from app.schemas import DocumentCreate, DocumentRead, QueryRequest, QueryResponse, QueryResult
from app.vectorstore import get_vector_store
from app.workers.queue import job_queue
from app.workers.tasks import process_document

app = FastAPI(title="Conduit")


@app.on_event("startup")
async def start_worker_queue():
    await job_queue.start()


@app.on_event("shutdown")
async def stop_worker_queue():
    await job_queue.stop()


@app.get("/health")
def health():
    return {"status": "ok", "db": settings.database_url}


@app.post("/documents", response_model=DocumentRead)
async def ingest_document(payload: DocumentCreate, session: AsyncSession = Depends(get_session)):
    document = Document(title=payload.title, content=payload.content)
    session.add(document)
    await session.commit()

    await job_queue.enqueue(lambda: process_document(document.id))

    return document


@app.get("/documents/{doc_id}", response_model=DocumentRead)
async def get_document(doc_id: int, session: AsyncSession = Depends(get_session)):
    document = await session.get(Document, doc_id)
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
