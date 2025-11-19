from app.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    if not text:
        return []

    size = chunk_size if chunk_size is not None else settings.chunk_size
    overlap_value = overlap if overlap is not None else settings.chunk_overlap

    # overlap >= size used to silently produce zero chunks (range() with a
    # step <= 0 just comes back empty), which meant an ingested document
    # would show as "indexed" with nothing actually searchable
    step = max(size - overlap_value, 1)

    return [text[i : i + size] for i in range(0, len(text), step)]
