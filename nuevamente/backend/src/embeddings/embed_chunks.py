"""Embebido de una lista de chunks (BE-RAG-005, OUT-004).

Esta función es el pegamento que conecta la ingesta con el vectorstore:
recibe los chunks ya procesados, usa el proveedor configurado para generar
sus vectores y los devuelve en el mismo orden.
"""
from src.core.exceptions import NuevaMenteError
from src.embeddings.base import EmbeddingProvider
from src.processing.models import DocumentChunk


def embed_chunks(
    chunks: list[DocumentChunk],
    provider: EmbeddingProvider,
) -> list[list[float]]:
    """Genera un vector por cada chunk, en el mismo orden.

    Lanza:
        NuevaMenteError: si el proveedor falla al generar embeddings
        (OUT-004 — manejo de error de embeddings).
    """
    if not chunks:
        return []
    texts = [chunk.text for chunk in chunks]
    try:
        return provider.embed_documents(texts)
    except Exception as exc:
        raise NuevaMenteError(f"Fallo al generar embeddings: {exc}") from exc