from fastapi import FastAPI, HTTPException

from app.config import settings

app = FastAPI(title="Conduit")

# quick in-memory stub so we can poke the endpoint before the db is wired up
_documents = {}


@app.get("/health")
def health():
    return {"status": "ok", "db": settings.database_url}


@app.post("/documents")
def ingest_document(payload: dict):
    doc_id = len(_documents) + 1
    _documents[doc_id] = payload
    return {"id": doc_id, "status": "received"}


@app.get("/documents/{doc_id}")
def get_document(doc_id: int):
    if doc_id not in _documents:
        raise HTTPException(status_code=404, detail="document not found")
    return _documents[doc_id]
