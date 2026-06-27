"""fastembed embedding wrapper — uses ONNX Runtime, no PyTorch, ~80MB RAM."""
import asyncio
from functools import lru_cache
from fastembed import TextEmbedding
from app.database.chroma_client import ChromaClient


@lru_cache(maxsize=1)
def _model() -> TextEmbedding:
    return TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    loop = asyncio.get_event_loop()
    vectors = await loop.run_in_executor(
        None, lambda: [v.tolist() for v in _model().embed(texts)]
    )
    return vectors


async def embed_query(query: str) -> list[float]:
    vectors = await embed_texts([query])
    return vectors[0] if vectors else []


async def embed_and_upsert_clauses(chroma: ChromaClient, clauses: list[dict]) -> int:
    if not clauses:
        return 0
    texts = [c["text"] for c in clauses]
    embeddings = await embed_texts(texts)
    ids = [c["clause_id"] for c in clauses]
    metas = [
        {"contract_id": c["contract_id"], "section": c["section"], "clause_id": c["clause_id"]}
        for c in clauses
    ]
    chroma.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metas)
    return len(clauses)
