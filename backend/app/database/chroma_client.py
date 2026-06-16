"""ChromaDB in-memory client — no external server required."""
import chromadb
from app.config import get_settings


class ChromaClient:
    def __init__(self, client: chromadb.ClientAPI, collection_name: str):
        self._client = client
        self._collection_name = collection_name

    @property
    def collection(self):
        return self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def ping(self) -> bool:
        try:
            self._client.heartbeat()
            return True
        except Exception:
            return False

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where: dict | None = None,
    ) -> dict:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )


_client: ChromaClient | None = None


def get_chroma() -> ChromaClient:
    global _client
    if _client is None:
        settings = get_settings()
        chroma = chromadb.EphemeralClient()
        _client = ChromaClient(chroma, settings.chroma_collection)
    return _client
