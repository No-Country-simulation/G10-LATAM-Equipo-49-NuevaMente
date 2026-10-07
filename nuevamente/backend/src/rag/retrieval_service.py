"""Retrieval service (BE-RAG-009, COMP-05).

Combina `EmbeddingProvider.embed_query` + `VectorStore.query` para obtener
el contexto relevante a una solicitud de adaptación.
"""
from src.core.config import get_settings
from src.embeddings.base import EmbeddingProvider
from src.embeddings.factory import get_embedding_provider
from src.vectorstore.base import VectorStore, VectorStoreMatch
from src.vectorstore.factory import get_vectorstore


class DefaultRetrievalService:
    """Implementación de `RetrievalService` sobre el vectorstore dado.

    Construye la query a partir de `perfil`/`nicho`/`tema` y recupera el
    top-k de chunks (`settings.RETRIEVAL_TOP_K`).

    Tanto el store como el embedder son inyectables para poder testear sin
    tocar los singletons. Por defecto se resuelven vía los factories, de modo
    que el servicio comparte el store con la ingesta.

    Nota: no conviene instanciar esto una sola vez a nivel de módulo, porque
    quedaría con una referencia fija al store cacheado. Se construye por
    solicitud (es barato: solo guarda referencias).
    """

    def __init__(
        self,
        store: VectorStore | None = None,
        embedder: EmbeddingProvider | None = None,
    ) -> None:
        self._store = store if store is not None else get_vectorstore()
        self._embedder = embedder if embedder is not None else get_embedding_provider()

    def retrieve(
        self,
        doc_id: str,
        perfil: str,
        nicho: str | None = None,
        tema: str | None = None,
    ) -> list[VectorStoreMatch]:
        settings = get_settings()
        query = " ".join(t for t in (perfil, nicho, tema) if t).strip() or "general"
        vector = self._embedder.embed_query(query)
        return self._store.query(vector, settings.RETRIEVAL_TOP_K, doc_id=doc_id)
