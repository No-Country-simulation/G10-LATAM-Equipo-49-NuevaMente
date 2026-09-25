from src.processing.models import DocumentChunk
from src.core.exceptions import NuevaMenteError
from src.core.logging import get_logger

log = get_logger(__name__)


def embed_chunks(chunks: list[DocumentChunk], provider) -> list[list[float]]:
    if not chunks:
        return []
    try:
        return provider.embed_documents([c.text for c in chunks])
    except Exception as exc:  # noqa: BLE001 — se traduce a error de dominio
        log.error("embedding_failed", error=str(exc))
        raise NuevaMenteError("Fallo al generar embeddings") from exc
