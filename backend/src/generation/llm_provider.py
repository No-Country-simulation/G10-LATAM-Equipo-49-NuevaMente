"""Contrato del proveedor de LLM (COMP-06) + implementaciones.

DT-09: Gemini propuesto (🔴 bloqueante, no confirmado formalmente — Plan
Técnico Fase 10/20). El resto del pipeline solo depende de `LLMProvider`,
nunca de un SDK concreto (RNF-005). El modo mock es determinista y sin red,
para que el vertical slice funcione sin credenciales (TESTING_STRATEGY).
"""
from typing import Protocol


class LLMProvider(Protocol):
    """Genera texto a partir de un prompt, con temperatura configurable."""

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Invoca al modelo de lenguaje.

        Lanza:
            LLMProviderError: ante timeout, error de API o cuota agotada
                (Fase 14 — timeout sugerido 30s, 1 reintento).
        """
        ...


class GeminiLLMProvider:
    """Implementación futura sobre Google Gemini API.

    # TODO: implementación futura — NO realizar llamadas reales al SDK de
    # Gemini en esta fase (CONTRACT-ONLY).
    """

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        ...


class MockLLMProvider:
    """Implementación determinista en modo mock, sin red.

    No produce texto real: eco estructurado del prompt recortado. Es el
    proveedor por defecto (`settings.LLM_PROVIDER=mock`) para desarrollo,
    tests y CI sin API key.
    """

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        return f"[mock:{temperature:.1f}] " + prompt[:400]