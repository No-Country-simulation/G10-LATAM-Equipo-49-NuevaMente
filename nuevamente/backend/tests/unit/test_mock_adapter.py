"""Adaptación mock: usa chunks reales, sin inventar contenido."""
from src.generation.mock_adapter import MOCK_NOTICE, build_mock_content
from src.processing.models import DocumentChunk


def _chunks(n: int) -> list[DocumentChunk]:
    return [
        DocumentChunk(
            id=f"doc_a-chunk-{i}",
            doc_id="doc_a",
            text=f"contenido numero {i} " * 5,
            position=i,
            section="Intro" if i < 2 else "Detalles",
            page=i + 1,
            char_start=i * 100,
            char_end=i * 100 + 50,
        )
        for i in range(n)
    ]


def test_chunks_used_is_fixed_at_three():
    chunks = _chunks(8)
    assert len(
        build_mock_content(
            "Principiante / Transición de Carrera",
            "Guía Práctica Paso a Paso (Tutorial)",
            "General",
            chunks,
        )[1]
    ) == 3


def test_content_cites_real_chunks_and_flags_mock_mode():
    profile = "Principiante / Transición de Carrera"
    content, used = build_mock_content(
        profile, "Guía Práctica Paso a Paso (Tutorial)", "Fintech", _chunks(4)
    )
    assert MOCK_NOTICE in content.cuerpo
    assert profile in content.cuerpo and "Fintech" in content.cuerpo
    assert "doc_a-chunk-0" in content.cuerpo
    assert "pág. 1" in content.cuerpo
    assert [c.id for c in used] == ["doc_a-chunk-0", "doc_a-chunk-1", "doc_a-chunk-2"]
    assert content.conceptos_clave == ["Intro", "Detalles"]
    assert content.tiempo_estimado_min >= 1


def test_long_excerpts_are_truncated():
    long_chunk = _chunks(1)[0].model_copy(update={"text": "palabra " * 500})
    content, _ = build_mock_content(
        "Principiante / Transición de Carrera",
        "Guía Práctica Paso a Paso (Tutorial)",
        "General",
        [long_chunk],
    )
    assert "…" in content.cuerpo
    assert len(content.cuerpo) < 1200
