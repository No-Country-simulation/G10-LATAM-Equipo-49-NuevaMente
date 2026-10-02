"""Orquestador de generación adaptada (BE-GEN-003, GEN-004, GEN-005).

Subtareas (Fase 8 del Plan Técnico):
    BE-GEN-003b — invocar `LLMProvider.generate(...)` con manejo de timeout/retry
    BE-GEN-003c — mapear la respuesta del LLM a `ContenidoAdaptado`

En modo mock (por defecto, sin credenciales), construye los items
pedagógicos tipados desde el contexto con los builders; el `cuerpo` queda
como el texto plano de los items.
"""
from src.core.config import get_settings
from src.generation.builders import build_contexto_items
from src.generation.llm_provider import LLMProvider, MockLLMProvider
from src.generation.models import AdaptationRequest, ContenidoAdaptado
from src.generation.profiles import conceptos_clave


class GenerationOrchestrator:
    """Flujo de generación adaptada (determinista en modo mock)."""

    def generate_content(
        self,
        request: AdaptationRequest,
        contexto: str,
        provider: LLMProvider | None = None,
    ) -> ContenidoAdaptado:
        """Genera contenido adaptado a partir de `contexto` y los parámetros
        de `request`. Precondición: `contexto` no vacío (garantizado por
        `rag.context_builder.build_context`)."""
        settings = get_settings()
        provider = provider or MockLLMProvider() if settings.LLM_PROVIDER == "mock" else provider

        items = build_contexto_items(contexto, request.formato, request.perfil)
        if items:
            cuerpo = "\n".join(i.model_dump_json() for i in items)
        elif provider is not None:
            cuerpo = provider.generate(contexto)
        else:
            cuerpo = contexto

        return ContenidoAdaptado(
            cuerpo=cuerpo,
            conceptos_clave=conceptos_clave(contexto, n=4),
            prerrequisitos=[],
            tiempo_estimado_min=max(1, len(items) * 2 + 3),
        )