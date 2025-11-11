from app.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    if not text:
        return []

    size = chunk_size if chunk_size is not None else settings.chunk_size
    step = size - (overlap if overlap is not None else settings.chunk_overlap)

    return [text[i : i + size] for i in range(0, len(text), step)]
