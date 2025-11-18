import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.db.session as db_session
import app.vectorstore as vectorstore
import app.workers.tasks as worker_tasks
from app.db.base import Base
from tests.fakes import FakeVectorStore


@pytest.fixture(autouse=True)
def fake_vector_store(monkeypatch):
    fake = FakeVectorStore()
    monkeypatch.setattr(vectorstore, "_store", fake)
    yield fake


@pytest_asyncio.fixture
async def test_engine(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # both modules imported `async_session` by name at import time, so the
    # dependency and the background worker each need their own patch
    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "async_session", session_factory)
    monkeypatch.setattr(worker_tasks, "async_session", session_factory)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine):
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        async with app.router.lifespan_context(app):
            yield http_client
