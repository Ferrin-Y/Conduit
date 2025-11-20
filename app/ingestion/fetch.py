import httpx

_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    # a client per request would open a new connection (and redo TLS) every
    # time; keeping one around lets httpx reuse the pool across requests
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _client


async def close_http_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def fetch_url_text(url: str) -> str:
    client = get_http_client()
    response = await client.get(url)
    response.raise_for_status()
    return response.text
