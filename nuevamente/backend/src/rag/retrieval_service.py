"""Retrieval service (BE-RAG-009, COMP-05).

Combina `EmbeddingProvider.embed_query` + `similarity_search` para obtener
el contexto relevante a una solicitud de adaptación.
"""
from src.core.config import get_settings
from src.embeddings.base import EmbeddingProvider
from src.embeddings.factory import get_embedding_provider
from src.vectorstore.base import VectorStore, VectorStoreMatch
from src.vectorstore.factory import get_vectorstore
from src.vectorstore.search import similarity_search


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
        # *********************************************************************
        #  MEJORA AUD-001 — 2026-10-15
        #  Antes la query SIEMPRE incluía el `perfil` y, en el orquestador, el
        #  inicio del documento; el tema pedido por el usuario no influía. Ahora,
        #  cuando hay `tema`, la consulta se construye con el tema (+ nicho) y el
        #  perfil queda como pista solo cuando NO hay tema (el perfil describe el
        #  estilo del destinatario, no el contenido a recuperar).
        # *********************************************************************
        settings = get_settings()
        parts = [tema, nicho] if tema else [perfil, nicho]
        query = " ".join(t for t in parts if t).strip() or "general"
        vector = self._embedder.embed_query(query)
        # similarity_search aplica el umbral de RETRIEVAL_MIN_SCORE y
        # envuelve fallos del store en VectorStoreError (OUT-005).
        return similarity_search(
            vector, self._store, settings.RETRIEVAL_TOP_K, doc_id=doc_id
        )
