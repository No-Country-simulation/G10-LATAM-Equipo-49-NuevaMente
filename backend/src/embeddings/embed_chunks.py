"""Embebido de una lista de chunks (BE-RAG-005, OUT-004)."""
from src.embeddings.base import EmbeddingProvider
from src.processing.models import DocumentChunk


def embed_chunks(
    chunks: list[DocumentChunk],
    provider: EmbeddingProvider,
) -> list[list[float]]:
    """Genera un vector por cada chunk, en el mismo orden.

    Lanza:
        NuevaMenteError (o una excepción más específica, a definir en la
        implementación): si el proveedor falla al generar embeddings
        (OUT-004 — manejo de error de embeddings).

    Implementación futura.
    """
    ...
