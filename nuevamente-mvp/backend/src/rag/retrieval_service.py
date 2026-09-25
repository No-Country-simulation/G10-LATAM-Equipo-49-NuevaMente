from src.vectorstore.search import search, RetrievedChunk
from src.core.config import settings


class RetrievalService:
    def __init__(self, embedding_provider):
        self.embedding_provider = embedding_provider

    def retrieve(self, document_id: str, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        top_k = top_k or settings.RETRIEVAL_TOP_K
        query_embedding = self.embedding_provider.embed_query(query)
        results = search(document_id=document_id, query_embedding=query_embedding, top_k=top_k)
        # distance más bajo = más similar (Chroma usa distancia, no score directo)
        return [r for r in results if r.distance <= (1 - settings.RETRIEVAL_MIN_SCORE) * 2]
