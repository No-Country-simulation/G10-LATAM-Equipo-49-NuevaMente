"""Adaptación MOCK de contenido (sin LLM ni RAG) — contrato `/adapt` de Semana 1.

Construye una vista previa determinista a partir de los PRIMEROS chunks reales
del documento ingerido, para poder probar el flujo completo (subir → elegir →
resultado) antes de integrar retrieval y Gemini (Semana 2). No inventa
contenido: solo cita fragmentos del documento con su trazabilidad.
"""
import math

from src.generation.models import ContenidoAdaptado
from src.processing.models import DocumentChunk

_CHUNKS_PER_ADAPTATION = 3
_EXCERPT_CHARS = 400
_WORDS_PER_MINUTE = 200
MOCK_NOTICE = (
    "Modo mock: el contenido muestra fragmentos del documento, sin adaptación por IA "
    "ni validación de fidelidad (RAG y LLM pendientes)."
)


def _excerpt(text: str) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= _EXCERPT_CHARS else flat[:_EXCERPT_CHARS].rstrip() + "…"


def _reference(chunk: DocumentChunk) -> str:
    parts = [chunk.id]
    if chunk.page is not None:
        parts.append(f"pág. {chunk.page}")
    if chunk.section:
        parts.append(chunk.section)
    return " · ".join(parts)


def build_mock_content(
    perfil: str,
    formato: str,
    nicho: str | None,
    chunks: list[DocumentChunk],
) -> tuple[ContenidoAdaptado, list[DocumentChunk]]:
    """Devuelve el contenido mock y los chunks fuente utilizados."""
    used = chunks[:_CHUNKS_PER_ADAPTATION]

    lines = [
        f"> ⚠️ {MOCK_NOTICE}",
        "",
        f"## Vista previa · perfil **{perfil}** · formato **{formato}**",
    ]
    if nicho:
        lines.append(f"Nicho / contexto: *{nicho}*")
    lines += ["", "### Fragmentos fuente"]
    for chunk in used:
        lines += ["", f"**[{_reference(chunk)}]**", "", f"> {_excerpt(chunk.text)}"]

    words = sum(len(c.text.split()) for c in used)
    sections: list[str] = []
    for chunk in used:
        if chunk.section and chunk.section not in sections:
            sections.append(chunk.section)

    content = ContenidoAdaptado(
        cuerpo="\n".join(lines),
        conceptos_clave=sections[:5],
        prerrequisitos=[],
        tiempo_estimado_min=max(1, math.ceil(words / _WORDS_PER_MINUTE)),
    )
    return content, used
