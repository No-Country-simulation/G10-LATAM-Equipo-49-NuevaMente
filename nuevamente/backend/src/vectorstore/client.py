"""Inicialización del cliente de ChromaDB embebido (BE-RAG-006, DT-02).

Persistencia en `settings.CHROMA_PERSIST_DIR`. Implementación futura — no
se realiza ninguna conexión real en esta fase (CONTRACT-ONLY).
"""
from typing import Any


def get_chroma_client() -> Any:
    """Devuelve (o crea) el cliente persistente de ChromaDB.

    Implementación futura.
    """
    ...
