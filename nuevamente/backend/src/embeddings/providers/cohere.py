"""Implementación de `EmbeddingProvider` con Cohere API (DT-09).

Usa `cohere` SDK v2. Llamadas en lotes de 96 (límite de la API),
reintentos con backoff exponencial, y traducción de errores a
`LLMProviderError` para que `embed_chunks` los envuelva en `NuevaMenteError`.

El modelo por defecto es `embed-multilingual-v3.0` que produce 1024 dimensiones.
`input_type` se usa semánticamente: "search_document" para documentos,
"search_query" para consultas.
"""
import time
from typing import Any

from src.core.config import get_settings
from src.core.exceptions import LLMProviderError


class CohereEmbeddingProvider:
    """Cumple el contrato `EmbeddingProvider` invocando la API de Cohere."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.COHERE_API_KEY
        self._model = model or settings.COHERE_EMBEDDING_MODEL
        self._timeout = timeout or settings.LLM_TIMEOUT_SECONDS
        self._max_retries = (
            max_retries if max_retries is not None else settings.LLM_MAX_RETRIES
        )
        self._client: Any = None

    def _get_client(self) -> Any:
        """Importación perezosa del cliente de Cohere."""
        if self._client is None:
            import cohere

            self._client = cohere.ClientV2(api_key=self._api_key)
        return self._client

    def _embed_with_retry(
        self, texts: list[str], input_type: str
    ) -> list[list[float]]:
        """Genera embeddings con reintentos y backoff exponencial."""
        client = self._get_client()
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = client.embed(
                    texts=texts,
                    model=self._model,
                    input_type=input_type,
                    embedding_types=["float"],
                )
                # Cohere v2 devuelve embeddings en response.embeddings.float_
                return response.embeddings.float_
            except Exception as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    wait = 2**attempt
                    time.sleep(wait)
                continue

        msg = (
            f"Fallo al generar embeddings tras {self._max_retries + 1} intentos: "
            f"{last_exc}"
        )
        raise LLMProviderError(msg) from last_exc

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Genera un vector por cada texto en `texts`, en el mismo orden.

        Procesa en lotes de 96 (límite de `/v2/embed` de Cohere).
        Usa `input_type="search_document"` para documentos.
        """
        if not texts:
            return []

        batch_size = 96
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = self._embed_with_retry(batch, "search_document")
            all_embeddings.extend(embeddings)

        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        """Genera el vector de una consulta individual (para retrieval).

        Usa `input_type="search_query"` para consultas.
        """
        return self._embed_with_retry([text], "search_query")[0]


# Nota: cumple el Protocol correspondiente por forma estructural (duck typing).
# No se usa issubclass() en importación: el Protocol no es @runtime_checkable.