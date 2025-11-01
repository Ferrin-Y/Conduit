CHUNK_SIZE = 500
CHUNK_OVERLAP = 50  # TODO: tune this, picked semi-arbitrarily


def chunk_text(text: str) -> list[str]:
    if not text:
        return []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    return [text[i : i + CHUNK_SIZE] for i in range(0, len(text), step)]
