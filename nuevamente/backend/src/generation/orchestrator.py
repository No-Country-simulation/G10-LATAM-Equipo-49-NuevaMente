"""Orquestador de generación adaptada (BE-GEN-003, GEN-004, GEN-005)."""
import json

from pydantic import ValidationError

from src.core.exceptions import LLMProviderError
from src.generation.llm_provider import LLMProvider
from src.generation.models import AdaptationRequest, ContenidoAdaptado
from src.generation.prompt_loader import (
    build_generation_prompt,
    strip_markdown_fences,
)


class GenerationOrchestrator:
    """Flujo de generación adaptada con parseo y validación estricta."""

    def generate_content(
        self,
        request: AdaptationRequest,
        contexto: str,
        provider: LLMProvider,
    ) -> ContenidoAdaptado:
        """Genera, parsea y valida contenido adaptado a partir de contexto."""
        nivel = (
            getattr(request, "nivel", None)
            or getattr(request, "nivel_detalle", None)
            or "estandar"
        )
        system_prompt, user_prompt = build_generation_prompt(
            contexto=contexto,
            perfil=request.perfil,
            formato=request.formato,
            nicho=request.nicho,
            nivel=nivel,
        )
        prompt = f"{system_prompt}\n\n{user_prompt}".strip()

        try:
            raw_response = provider.generate(prompt)
        except LLMProviderError:
            raise
        except Exception as exc:  # pragma: no cover - defensa adicional
            raise LLMProviderError(f"Error inesperado del proveedor LLM: {exc}") from exc

        if not raw_response or not raw_response.strip():
            raise LLMProviderError("El proveedor LLM devolvió una respuesta vacía.")

        cleaned_response = strip_markdown_fences(raw_response)
        if not cleaned_response:
            raise LLMProviderError(
                "La respuesta del proveedor quedó vacía tras limpiar markdown."
            )

        try:
            payload = json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise LLMProviderError("La respuesta del proveedor no es JSON válido.") from exc
        if not isinstance(payload, dict):
            raise LLMProviderError("La respuesta del proveedor debe ser un objeto JSON.")

        try:
            content = ContenidoAdaptado.model_validate(payload)
        except ValidationError as exc:
            raise LLMProviderError(
                "La respuesta del proveedor no cumple el esquema esperado."
            ) from exc

        if not content.cuerpo.strip():
            raise LLMProviderError("La respuesta del proveedor tiene `cuerpo` vacío.")
        return content
