from app.ingestion.chunking import chunk_text


def test_chunk_text_respects_explicit_size_with_no_overlap():
    text = "a" * 1010
    chunks = chunk_text(text, chunk_size=500, overlap=0)
    assert len(chunks) == 3
    assert len(chunks[0]) == 500
    assert len(chunks[-1]) == 10


def test_chunk_text_overlap_shrinks_the_step():
    text = "a" * 1000
    no_overlap = chunk_text(text, chunk_size=500, overlap=0)
    with_overlap = chunk_text(text, chunk_size=500, overlap=50)
    assert len(with_overlap) > len(no_overlap)


def test_chunk_text_short_input_single_chunk():
    chunks = chunk_text("hello world", chunk_size=500, overlap=50)
    assert chunks == ["hello world"]


def test_chunk_text_empty_input():
    assert chunk_text("") == []
