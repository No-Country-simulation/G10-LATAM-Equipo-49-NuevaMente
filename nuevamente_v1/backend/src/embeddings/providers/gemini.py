"""Implementación futura de `EmbeddingProvider` con Google Gemini API (free
tier), DT-09. 🔴 Proveedor pendiente de confirmación formal por el equipo.

# TODO: implementación futura — NO realizar llamadas reales al SDK de
# Gemini en esta fase (CONTRACT-ONLY).
"""
from src.embeddings.base import EmbeddingProvider


class GeminiEmbeddingProvider:
    """Cumple el contrato `EmbeddingProvider` invocando la API de Gemini.

    Se declara la clase para dejar explícito el punto de integración
    futuro; ningún método tiene lógica ni realiza llamadas de red.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...
# Nota: cumple el Protocol correspondiente por forma estructural (duck typing) — no se usa issubclass() en tiempo de importación porque el Protocol no está marcado @runtime_checkable.
