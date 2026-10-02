"""Implementación futura de `EmbeddingProvider` en modo mock, para poder
desarrollar y probar el resto del pipeline sin credenciales reales.

# TODO: implementación futura — sin lógica real todavía.
"""


class MockEmbeddingProvider:
    """Cumple el contrato `EmbeddingProvider` sin llamar a ningún servicio
    externo. Debe ser determinista (mismo texto → mismo vector) una vez
    implementado, para que los tests puedan ser reproducibles.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...

