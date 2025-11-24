# Conduit

Async document ingestion and semantic vector retrieval engine. Built for RAG
pipelines: documents go in over HTTP, get chunked and embedded off the
request thread by a background worker pool, and land in a vector store you
can query semantically.

## Why

Most "ingest a doc and embed it" examples do the parsing and embedding
inline in the request handler. That's fine for a demo and terrible under
load — a slow parse or a slow embedding call blocks the connection it came
in on. Conduit decouples ingestion from indexing: `POST /documents` returns
as soon as the row is written, and an `asyncio` worker pool does the actual
chunking + embedding + indexing in the background.

## Stack

- FastAPI + Pydantic v2 for the API layer
- SQLAlchemy 2.0 (async) + Alembic for the document/chunk metadata
- ChromaDB for vector storage and similarity search, behind a small
  `VectorStore` interface so it can be swapped out
- httpx for pulling in documents by URL
- pytest + pytest-asyncio for tests, Ruff for linting/formatting

## Running it

### Docker (recommended)

```bash
docker compose up --build
```

The API comes up on `http://localhost:8000`.

### Locally

```bash
python -m venv .venv
.venv/Scripts/activate  # or source .venv/bin/activate on macOS/Linux
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

> **Windows note:** `chromadb==0.5.15` pins `chroma-hnswlib==0.7.6`, which
> doesn't ship a Windows wheel for Python 3.12 — pip will try to build it
> from source and fail without the MSVC build tools. Easiest fix is to
> run inside Docker (the `python:3.11-slim` image has manylinux wheels),
> or install the [MSVC Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
> if you want it working natively. The app itself doesn't import
> `chromadb` until a document is actually processed, so everything else
> (API, db, chunking, tests with a fake vector store) works fine either way.

## API

```
POST /documents
  { "title": "...", "content": "..." }       # inline text, or
  { "title": "...", "source_url": "..." }    # fetched over http
  -> { "id": 1, "title": "...", "status": "pending" }

GET /documents/{id}
  -> { "id": 1, "title": "...", "status": "indexed" }

POST /query
  { "query": "...", "top_k": 5 }
  -> { "results": [ { "text": "...", "distance": 0.12, "document_id": 1 } ] }
```

Document status moves `pending -> processing -> indexed` (or `failed`) as
the background worker picks it up, chunks the content, and pushes the
chunks into the vector store.

## Development

```bash
pytest
ruff check .
ruff format .
```
