"""Health endpoint."""
from fastapi import APIRouter
from app.database.neo4j_client import get_neo4j
from app.database.chroma_client import get_chroma

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health():
    neo4j = await get_neo4j()
    chroma = get_chroma()
    neo_ok = neo4j.ping()
    chr_ok = chroma.ping()
    status = "healthy" if neo_ok and chr_ok else "degraded"
    return {
        "status": status,
        "neo4j": "ok" if neo_ok else "error",
        "chroma": "ok" if chr_ok else "error",
    }
