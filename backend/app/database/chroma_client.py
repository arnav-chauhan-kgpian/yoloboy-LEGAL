"""ChromaDB stub — disabled to stay within Railway 512MB RAM limit."""


class ChromaClient:
    def ping(self) -> bool:
        return True

    def upsert(self, ids, embeddings, documents, metadatas) -> None:
        pass

    def query(self, query_embedding, n_results=10, where=None) -> dict:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}


_client: ChromaClient | None = None


def get_chroma() -> ChromaClient:
    global _client
    if _client is None:
        _client = ChromaClient()
    return _client
