async def test_query_returns_matching_chunks(client, fake_vector_store):
    fake_vector_store.add(
        ids=["1", "2"],
        texts=["the quick brown fox", "something unrelated entirely"],
        metadatas=[{"document_id": 1, "chunk_index": 0}, {"document_id": 2, "chunk_index": 0}],
    )

    r = await client.post("/query", json={"query": "fox", "top_k": 5})
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 1
    assert results[0]["document_id"] == 1


async def test_query_respects_top_k(client, fake_vector_store):
    fake_vector_store.add(
        ids=[str(i) for i in range(10)],
        texts=["match " + str(i) for i in range(10)],
        metadatas=[{"document_id": i} for i in range(10)],
    )

    r = await client.post("/query", json={"query": "match", "top_k": 3})
    assert len(r.json()["results"]) == 3


async def test_query_rejects_invalid_top_k(client):
    r = await client.post("/query", json={"query": "fox", "top_k": 0})
    assert r.status_code == 422
