from dataclasses import dataclass
from src.vectorstore.search import RetrievedChunk


@dataclass
class BuiltContext:
    text: str
    chunk_ids: list[str]
    sources: list[dict]  # [{chunk_id, page}]


def build_query(profile: str, format_: str, niche: str | None, detail_level: str) -> str:
    niche_part = f" en el contexto {niche}" if niche else ""
    return (
        f"Perfil: {profile}\nFormato: {format_}\nNivel: {detail_level}\n\n"
        f"Necesito explicar los conceptos fundamentales del documento "
        f"para una persona con perfil {profile}{niche_part}."
    )


def build_context(chunks: list[RetrievedChunk]) -> BuiltContext | None:
    """Retorna None si no hay contexto suficiente -> regla NO_CONTEXT (BE-RAG-011)."""
    if not chunks:
        return None

    parts = []
    sources = []
    for c in chunks:
        header = f"[CHUNK {c.chunk_id}" + (f" | PAGE {c.page}" if c.page else "") + "]"
        parts.append(f"{header}\n\n{c.text}")
        sources.append({"chunk_id": c.chunk_id, "page": c.page})

    return BuiltContext(text="\n\n".join(parts), chunk_ids=[c.chunk_id for c in chunks], sources=sources)
