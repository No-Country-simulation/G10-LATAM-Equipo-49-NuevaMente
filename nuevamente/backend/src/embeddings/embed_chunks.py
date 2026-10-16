"""Embebido de una lista de chunks (BE-RAG-005, OUT-004).

Esta función es el pegamento que conecta la ingesta con el vectorstore:
recibe los chunks ya procesados, usa el proveedor configurado para generar
sus vectores y los devuelve en el mismo orden.
"""
from src.core.exceptions import EmbeddingError, NuevaMenteError
from src.embeddings.base import EmbeddingProvider
from src.processing.models import DocumentChunk


def embed_chunks(
    chunks: list[DocumentChunk],
    provider: EmbeddingProvider,
) -> list[list[float]]:
    """Genera un vector por cada chunk, en el mismo orden.

    *********************************************************************
    MEJORA AUD-014b — 2026-10-15
    Antes no se validaba la cantidad de vectores devueltos: un proveedor que
    devolvía menos vectores que chunks indexaba fragmentos ausentes sin error.
    Ahora se exige exactamente un vector por chunk.

    MEJORA AUD-022a — 2026-10-15
    Un error ya tipado del proveedor (`LLMProviderError`, 502) se propaga sin
    re-envolver; antes se degradaba a `NuevaMenteError` genérico (500) y se
    filtraba el texto crudo de la excepción. Los fallos no tipados se envuelven
    en `EmbeddingError` (`EMBEDDING_ERROR`, 502) conservando la causa.

    Lanza:
        NuevaMenteError (EmbeddingError o el error de dominio del proveedor) si
        el proveedor falla o devuelve una cantidad de vectores inconsistente
        (OUT-004 — manejo de error de embeddings).
    *********************************************************************
    """
    if not chunks:
        return []
    texts = [chunk.text for chunk in chunks]
    try:
        vectors = provider.embed_documents(texts)
    except NuevaMenteError:
        raise
    except Exception as exc:
        raise EmbeddingError(f"Fallo al generar embeddings: {exc}") from exc

    if len(vectors) != len(chunks):
        raise EmbeddingError(
            f"El proveedor devolvió {len(vectors)} vectores para {len(chunks)} chunks."
        )
    return vectors
