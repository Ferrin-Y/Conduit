from fastapi import FastAPI

from app.config import settings

app = FastAPI(title="Conduit")


@app.get("/health")
def health():
    return {"status": "ok", "db": settings.database_url}
