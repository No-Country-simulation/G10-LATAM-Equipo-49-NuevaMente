from src.processing.models import DocumentChunk
from src.vectorstore.client import get_collection
from src.core.exceptions import NuevaMenteError
from src.core.logging import get_logger

log = get_logger(__name__)


def persist_chunks(chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
    if not chunks:
        return
    if len(chunks) != len(embeddings):
        raise NuevaMenteError("Cantidad de chunks y embeddings no coincide")

    try:
        collection = get_collection()
        collection.add(
            ids=[c.id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "doc_id": c.doc_id,
                    "position": c.position,
                    "page": c.page or 0,
                    "section": c.section or "",
                }
                for c in chunks
            ],
        )
        log.info("chunks_persisted", doc_id=chunks[0].doc_id, count=len(chunks))
    except Exception as exc:  # noqa: BLE001
        log.error("vectorstore_unavailable", error=str(exc))
        raise NuevaMenteError("Vector Store no disponible") from exc  # OUT-005
