"""Inicialización del cliente de ChromaDB embebido (BE-RAG-006, DT-02).

Persistencia en `settings.CHROMA_PERSIST_DIR`. La colección se nombra
según proveedor de embeddings y dimensiones para evitar conflictos
al cambiar de proveedor.
"""
import re
from functools import lru_cache
from typing import Any

from src.core.config import get_settings


@lru_cache
def get_chroma_client() -> Any:
    """Devuelve (o crea) el cliente persistente de ChromaDB."""
    import chromadb

    settings = get_settings()
    persist_dir = settings.resolve_path(settings.CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def _collection_name(settings) -> str:
    """Nombre de colección segregado por proveedor, modelo y dimensión real.

    *********************************************************************
    MEJORA AUD-012 — 2026-10-15
    Antes era `nuevamente_{provider}_{dims}`: cambiaba al cambiar de proveedor
    o dimensión, pero NO al cambiar de modelo de embeddings, y para el mock
    usaba una dimensión configurada (768) distinta de la real (256). Ahora el
    nombre incorpora proveedor + modelo + dimensión efectiva, de modo que dos
    espacios vectoriales incompatibles nunca comparten colección.
    *********************************************************************
    """
    provider = settings.EMBEDDING_PROVIDER.lower()
    dims = settings.active_embedding_dimensions
    model = re.sub(r"[^a-z0-9]+", "-", settings.active_embedding_model.lower()).strip("-")
    return f"nuevamente_{provider}_{model}_{dims}"


@lru_cache
def get_chroma_collection() -> Any:
    """Devuelve (o crea) la colección de ChromaDB para el proveedor actual."""
    client = get_chroma_client()
    settings = get_settings()
    name = _collection_name(settings)
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )