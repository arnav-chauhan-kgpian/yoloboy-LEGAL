"""Embedding stub — vector search disabled to stay within Railway 512MB RAM limit.
G2 gap detection (the core demo feature) is graph-only and unaffected."""


async def embed_texts(texts: list[str]) -> list[list[float]]:
    return []


async def embed_query(query: str) -> list[float]:
    return []


async def embed_and_upsert_clauses(chroma, clauses: list[dict]) -> int:
    return len(clauses)
