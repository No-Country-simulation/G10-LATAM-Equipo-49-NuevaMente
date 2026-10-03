"""Contrato del proveedor de LLM de generación (COMP-05).

Fuente: instrucciones de arquitectura + DT-09 (Gemini propuesto). Cualquier
proveedor concreto (Gemini, mock u otro) debe implementar este `Protocol` para
que el resto del pipeline (COMP-04, COMP-06) sea independiente del proveedor
(RNF-005).

Nota: el contrato de *embeddings* (`EmbeddingProvider`) vive en
`src/embeddings/base.py`. Este módulo es exclusivamente el de *generación*.
"""
from typing import Protocol


class LLMProvider(Protocol):
    """Genera texto a partir de un prompt."""

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Devuelve la respuesta del modelo para `prompt`.

        Lanza:
            LLMProviderError: si la llamada falla o agota los reintentos
                (traducida por la implementación, no por este contrato).

        Implementación futura.
        """
        ...
