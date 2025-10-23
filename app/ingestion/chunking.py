CHUNK_SIZE = 500


def chunk_text(text: str) -> list[str]:
    return [text[i : i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
