import asyncio


async def test_ingest_document_returns_pending_then_indexed(client):
    r = await client.post("/documents", json={"title": "t", "content": "hello world " * 60})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "pending"
    doc_id = body["id"]

    for _ in range(20):
        await asyncio.sleep(0.05)
        r2 = await client.get(f"/documents/{doc_id}")
        if r2.json()["status"] == "indexed":
            break
    else:
        raise AssertionError("document never reached indexed status")


async def test_get_document_not_found(client):
    r = await client.get("/documents/999")
    assert r.status_code == 404


async def test_ingest_document_rejects_empty_title(client):
    r = await client.post("/documents", json={"title": "", "content": "x"})
    assert r.status_code == 422


async def test_ingest_document_rejects_unknown_fields(client):
    r = await client.post("/documents", json={"title": "t", "content": "x", "unexpected": "nope"})
    assert r.status_code == 422


async def test_ingest_document_rejects_both_content_and_url(client):
    r = await client.post(
        "/documents",
        json={"title": "t", "content": "x", "source_url": "https://example.com/doc.txt"},
    )
    assert r.status_code == 422


async def test_ingest_document_fetches_from_url(client, monkeypatch):
    async def fake_fetch(url):
        assert url == "https://example.com/doc.txt"
        return "fetched content " * 10

    monkeypatch.setattr("app.main.fetch_url_text", fake_fetch)

    r = await client.post(
        "/documents", json={"title": "t", "source_url": "https://example.com/doc.txt"}
    )
    assert r.status_code == 200
