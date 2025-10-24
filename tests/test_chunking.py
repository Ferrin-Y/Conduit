from app.ingestion.chunking import CHUNK_SIZE, chunk_text


def test_chunk_text_splits_on_size():
    text = "a" * (CHUNK_SIZE * 2 + 10)
    chunks = chunk_text(text)
    assert len(chunks) == 3
    assert len(chunks[0]) == CHUNK_SIZE
    assert len(chunks[-1]) == 10


def test_chunk_text_short_input_single_chunk():
    chunks = chunk_text("hello world")
    assert chunks == ["hello world"]


def test_chunk_text_empty_input():
    assert chunk_text("") == []
