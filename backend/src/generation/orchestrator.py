"""Orquestador de generación adaptada (BE-GEN-003, GEN-004, GEN-005).

Subtareas previstas (Fase 8 del Plan Técnico):
    BE-GEN-003a — construir el prompt final combinando contexto + perfil/formato/nicho/detalle
    BE-GEN-003b — invocar `LLMProvider.generate(...)` con manejo de timeout/retry
    BE-GEN-003c — mapear la respuesta del LLM a `ContenidoAdaptado`
"""
from src.generation.llm_provider import LLMProvider
from src.generation.models import AdaptationRequest, ContenidoAdaptado


class GenerationOrchestrator:
    """Implementación futura del flujo de generación adaptada."""

    def generate_content(
        self,
        request: AdaptationRequest,
        contexto: str,
        provider: LLMProvider,
    ) -> ContenidoAdaptado:
        """Genera contenido adaptado a partir de `contexto` y los
        parámetros de `request`.

        Precondición: `contexto` no vacío (garantizado por
        `rag.context_builder.build_context`, que lanza `NoContextError`
        antes de llegar aquí si no lo está — regla PROMPT-001 "Fallback").

        Lanza:
            LLMProviderError: propagada desde `provider.generate(...)`.

        Implementación futura.
        """
        ...
