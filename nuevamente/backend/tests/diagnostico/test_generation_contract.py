"""Contrato de generación, prompt y schema específico por formato."""
import json

import pytest

from src.core.exceptions import LLMProviderError
from src.generation.models import AdaptationRequest, ContenidoAdaptado
from src.generation.orchestrator import GenerationOrchestrator
from src.generation.prompt_loader import PROMPTS_DIR

# CAMBIO H-01/H-04/H-05 INICIO — 2026-10-24


class FakeProvider:
    """Proveedor de LLM que registra el prompt y devuelve un JSON fijo."""

    def __init__(self, respuesta: str | None = None) -> None:
        self.prompts: list[str] = []
        self._respuesta = respuesta or json.dumps(
            {
                "cuerpo": "## Quiz\n\n1. ¿Qué es la autorización idempotente?",
                "conceptos_clave": ["idempotencia"],
                "prerrequisitos": [],
                "tiempo_estimado_min": 5,
                "preguntas": [
                    {
                        "pregunta": "¿Qué es la idempotencia?",
                        "opciones": ["Una propiedad"],
                        "respuesta_correcta": "Una propiedad",
                        "justificacion": "Se repite el resultado.",
                    }
                ],
            }
        )

    def generate(self, prompt: str, temperature: float = 0.3) -> str:  # noqa: ARG002
        self.prompts.append(prompt)
        return self._respuesta


REQUEST = AdaptationRequest(
    document_id="doc_demo",
    perfil="Líder Técnico / Arquitecto",
    formato="Quiz Interactivo con Justificaciones",
    nicho="Fintech",
)


def test_devuelve_un_contenido_adaptado_no_vacio() -> None:
    provider = FakeProvider()

    content = GenerationOrchestrator().generate_content(
        REQUEST, "Contexto técnico de Atlas Pay", provider
    )

    assert isinstance(content, ContenidoAdaptado)
    assert content.cuerpo.strip()


def test_invoca_al_proveedor_con_el_prompt_construido() -> None:
    provider = FakeProvider()

    GenerationOrchestrator().generate_content(
        REQUEST, "Contexto técnico de Atlas Pay", provider
    )

    assert provider.prompts, "generate_content() no llamó a provider.generate()"
    prompt = provider.prompts[0]
    assert REQUEST.formato in prompt


def test_el_prompt_pide_estructura_especifica_del_formato() -> None:
    provider = FakeProvider()

    GenerationOrchestrator().generate_content(
        REQUEST, "Contexto técnico de Atlas Pay", provider
    )

    assert provider.prompts, "generate_content() no llamó a provider.generate()"
    prompt = provider.prompts[0].lower()
    # Un quiz debe pedir preguntas + opciones + justificación, no solo un cuerpo.
    assert "pregunta" in prompt
    assert "justific" in prompt


def test_json_invalido_del_proveedor_lanza_llm_provider_error() -> None:
    provider = FakeProvider(respuesta="esto no es JSON")

    with pytest.raises(LLMProviderError):
        GenerationOrchestrator().generate_content(
            REQUEST, "Contexto técnico de Atlas Pay", provider
        )


def test_formato_sin_datos_estructurados_lanza_llm_provider_error() -> None:
    provider = FakeProvider(
        respuesta=json.dumps({"cuerpo": "texto", "preguntas": []})
    )

    with pytest.raises(LLMProviderError, match="contenido estructurado"):
        GenerationOrchestrator().generate_content(
            REQUEST, "Contexto técnico de Atlas Pay", provider
        )


def test_prompt_v1_incluye_estructura_por_formato() -> None:
    from src.generation.prompt_loader import build_generation_prompt

    raw = (PROMPTS_DIR / "generacion_v1.txt").read_text(encoding="utf-8")

    assert "{estructura_formato}" in raw
    assert "<!-- CAMBIO" not in raw
    for formato in (
        "Guía Práctica Paso a Paso (Tutorial)",
        "Flashcards de Memorización",
        "Quiz Interactivo con Justificaciones",
        "Resumen Ejecutivo (TL;DR)",
        "Guion de Clase / Video",
    ):
        system_prompt, user_prompt = build_generation_prompt(
            "contexto", "perfil", formato, "General"
        )
        prompt = f"{system_prompt}\n{user_prompt}"
        assert "ESTRUCTURA OBLIGATORIA" in prompt
        assert formato in prompt
        assert "<!-- CAMBIO" not in prompt


def test_schema_tiene_campos_especificos_para_los_formatos() -> None:
    campos = set(ContenidoAdaptado.model_fields)
    assert {"pasos", "tarjetas", "preguntas", "resumen_ejecutivo", "escenas"} <= campos
# CAMBIO H-01/H-04/H-05 FIN — 2026-10-24
