"""HuggingFace sentence-transformers embedding wrapper + clause embedding pipeline."""
import asyncio
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.config import get_settings
from app.database.chroma_client import ChromaClient


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    loop = asyncio.get_event_loop()
    vectors = await loop.run_in_executor(
        None, lambda: _model().encode(texts, convert_to_numpy=True).tolist()
    )
    return vectors


async def embed_query(query: str) -> list[float]:
    vectors = await embed_texts([query])
    return vectors[0] if vectors else []


async def embed_and_upsert_clauses(
    chroma: ChromaClient,
    clauses: list[dict],
) -> int:
    """
    clauses: list of {clause_id, contract_id, section, text}
    """
    if not clauses:
        return 0
    texts = [c["text"] for c in clauses]
    embeddings = await embed_texts(texts)
    ids = [c["clause_id"] for c in clauses]
    metas = [
        {
            "contract_id": c["contract_id"],
            "section": c["section"],
            "clause_id": c["clause_id"],
        }
        for c in clauses
    ]
    chroma.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metas,
    )
    return len(clauses)
