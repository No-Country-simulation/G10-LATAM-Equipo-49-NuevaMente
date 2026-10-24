"""Orquestador de generación adaptada (BE-GEN-003, GEN-004, GEN-005)."""
from pydantic import ValidationError

from src.core.exceptions import LLMProviderError
from src.generation.llm_provider import LLMProvider
from src.generation.models import AdaptationRequest, ContenidoAdaptado
from src.generation.prompt_loader import build_generation_prompt, strip_markdown_fences

# CAMBIO H-01/H-08 INICIO — 2026-10-24
_FORMAT_FIELDS = {
    "Guía Práctica Paso a Paso (Tutorial)": "pasos",
    "Flashcards de Memorización": "tarjetas",
    "Quiz Interactivo con Justificaciones": "preguntas",
    "Resumen Ejecutivo (TL;DR)": "resumen_ejecutivo",
    "Guion de Clase / Video": "escenas",
}


class GenerationOrchestrator:
    """Construye el prompt, invoca el proveedor y valida la respuesta."""

    def generate_content(
        self,
        request: AdaptationRequest,
        contexto: str,
        provider: LLMProvider,
    ) -> ContenidoAdaptado:
        """Genera contenido adaptado a partir de `contexto` y los
        parámetros de `request`.

        Lanza:
            LLMProviderError: si el proveedor falla o su respuesta no cumple
                el contrato JSON del formato solicitado.
        """
        if not contexto.strip():
            raise LLMProviderError("No se puede generar contenido sin contexto.")

        system_prompt, user_prompt = build_generation_prompt(
            contexto=contexto,
            perfil=request.perfil,
            formato=request.formato,
            nicho=request.nicho,
        )
        raw_response = provider.generate(f"{system_prompt}\n\n{user_prompt}")
        try:
            content = ContenidoAdaptado.model_validate_json(
                strip_markdown_fences(raw_response)
            )
        except (ValidationError, ValueError) as exc:
            raise LLMProviderError(
                "El proveedor devolvió una respuesta que no cumple el schema JSON."
            ) from exc

        required_field = _FORMAT_FIELDS[request.formato]
        value = getattr(content, required_field)
        if not value:
            raise LLMProviderError(
                f"La respuesta no incluye contenido estructurado para {request.formato}."
            )
        return content
# CAMBIO H-01/H-08 FIN — 2026-10-24


