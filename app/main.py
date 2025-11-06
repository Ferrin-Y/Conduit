from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.models import Document
from app.vectorstore import get_vector_store
from app.workers.queue import job_queue
from app.workers.tasks import process_document


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

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


@app.post("/documents")
async def ingest_document(payload: dict, session: AsyncSession = Depends(get_session)):
    document = Document(title=payload["title"], content=payload["content"])
    session.add(document)
    await session.commit()

    await job_queue.enqueue(lambda: process_document(document.id))

    return {"id": document.id, "status": "received"}


@app.get("/documents/{doc_id}")
async def get_document(doc_id: int, session: AsyncSession = Depends(get_session)):
    document = await session.get(Document, doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    return {
        "id": document.id,
        "title": document.title,
        "status": document.status,
    }


@app.post("/query")
def semantic_query(payload: QueryRequest):
    store = get_vector_store()
    results = store.query(payload.query, top_k=payload.top_k)
    return {
        "results": [
            {
                "text": r.text,
                "distance": r.distance,
                "document_id": r.metadata.get("document_id"),
            }
            for r in results
        ]
    }
