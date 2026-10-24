"""Tests unitarios del contrato de `GenerationOrchestrator`."""

import pytest

from src.core.exceptions import LLMProviderError
from src.generation.models import AdaptationRequest
from src.generation.orchestrator import GenerationOrchestrator


class _FakeProvider:
    def __init__(self, response: str | None = None, exc: Exception | None = None):
        self._response = response
        self._exc = exc
        self.calls: list[str] = []

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        self.calls.append(prompt)
        if self._exc is not None:
            raise self._exc
        return self._response or ""


def _request() -> AdaptationRequest:
    return AdaptationRequest(
        document_id="doc-1",
        perfil="Principiante / Transición de Carrera",
        formato="Guía Práctica Paso a Paso (Tutorial)",
        nicho="Fintech",
    )


def test_generate_content_builds_prompt_and_calls_provider(monkeypatch):
    captured: dict[str, str] = {}

    def _fake_build(contexto: str, perfil: str, formato: str, nicho: str, nivel: str):
        captured.update(
            {
                "contexto": contexto,
                "perfil": perfil,
                "formato": formato,
                "nicho": nicho,
                "nivel": nivel,
            }
        )
        return "SYS", "USR"

    monkeypatch.setattr("src.generation.orchestrator.build_generation_prompt", _fake_build)
    provider = _FakeProvider('{"cuerpo":"ok","conceptos_clave":[],"prerrequisitos":[]}')

    result = GenerationOrchestrator().generate_content(_request(), "contexto de prueba", provider)

    assert captured == {
        "contexto": "contexto de prueba",
        "perfil": "Principiante / Transición de Carrera",
        "formato": "Guía Práctica Paso a Paso (Tutorial)",
        "nicho": "Fintech",
        "nivel": "estandar",
    }
    assert provider.calls == ["SYS\n\nUSR"]
    assert result.cuerpo == "ok"


def test_generate_content_parses_valid_json():
    provider = _FakeProvider(
        '{"cuerpo":"contenido válido","conceptos_clave":["x"],'
        '"prerrequisitos":[],"tiempo_estimado_min":12}'
    )

    result = GenerationOrchestrator().generate_content(_request(), "ctx", provider)

    assert result.cuerpo == "contenido válido"
    assert result.conceptos_clave == ["x"]
    assert result.tiempo_estimado_min == 12


def test_generate_content_parses_json_inside_markdown_fences():
    provider = _FakeProvider(
        "```json\n"
        '{"cuerpo":"desde fence","conceptos_clave":[],"prerrequisitos":[]}'
        "\n```"
    )

    result = GenerationOrchestrator().generate_content(_request(), "ctx", provider)

    assert result.cuerpo == "desde fence"


def test_generate_content_rejects_empty_response():
    provider = _FakeProvider("   ")

    with pytest.raises(LLMProviderError, match="respuesta vacía"):
        GenerationOrchestrator().generate_content(_request(), "ctx", provider)


def test_generate_content_rejects_invalid_json():
    provider = _FakeProvider("{invalido")

    with pytest.raises(LLMProviderError, match="JSON válido"):
        GenerationOrchestrator().generate_content(_request(), "ctx", provider)


def test_generate_content_rejects_invalid_schema():
    provider = _FakeProvider('{"conceptos_clave":[],"prerrequisitos":[]}')

    with pytest.raises(LLMProviderError, match="esquema"):
        GenerationOrchestrator().generate_content(_request(), "ctx", provider)


def test_generate_content_rejects_empty_cuerpo():
    provider = _FakeProvider('{"cuerpo":"  ","conceptos_clave":[],"prerrequisitos":[]}')

    with pytest.raises(LLMProviderError, match="cuerpo"):
        GenerationOrchestrator().generate_content(_request(), "ctx", provider)


def test_generate_content_propagates_provider_error():
    provider = _FakeProvider(exc=LLMProviderError("falló proveedor"))

    with pytest.raises(LLMProviderError, match="falló proveedor"):
        GenerationOrchestrator().generate_content(_request(), "ctx", provider)
