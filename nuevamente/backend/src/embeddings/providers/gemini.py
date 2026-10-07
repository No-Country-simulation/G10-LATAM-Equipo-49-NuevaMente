"""Implementación de `EmbeddingProvider` con Google Gemini API (free tier), DT-09.

Usa `google-genai` SDK. Llamadas en lotes de 100 (límite de la API),
reintentos con backoff exponencial, y traducción de errores a
`LLMProviderError` para que `embed_chunks` los envuelva en `NuevaMenteError`
(cumple OUT-004).
"""
import time
from typing import Any

from src.core.config import get_settings
from src.core.exceptions import LLMProviderError


class GeminiEmbeddingProvider:
    """Cumple el contrato `EmbeddingProvider` invocando la API de Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model = model or settings.GEMINI_EMBEDDING_MODEL
        self._timeout = timeout or settings.LLM_TIMEOUT_SECONDS
        self._max_retries = max_retries if max_retries is not None else settings.LLM_MAX_RETRIES
        self._client: Any = None

    def _get_client(self) -> Any:
        """Importación perezosa del cliente de google-genai."""
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _embed_with_retry(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings con reintentos y backoff exponencial."""
        client = self._get_client()
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = client.models.embed_content(
                    model=self._model,
                    contents=texts,
                )
                # La API devuelve una lista de ContentEmbedding con .values
                return [emb.values for emb in response.embeddings]
            except Exception as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    wait = 2**attempt
                    time.sleep(wait)
                continue

        # Si llegamos aquí, todos los reintentos fallaron
        msg = f"Fallo al generar embeddings tras {self._max_retries + 1} intentos: {last_exc}"
        raise LLMProviderError(msg) from last_exc

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Genera un vector por cada texto en `texts`, en el mismo orden.

        Procesa en lotes de 100 (límite de la API de embeddings de Gemini).
        """
        if not texts:
            return []

        batch_size = 100
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = self._embed_with_retry(batch)
            all_embeddings.extend(embeddings)

        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        """Genera el vector de una consulta individual (para retrieval)."""
        return self.embed_documents([text])[0]


# Nota: cumple el Protocol correspondiente por forma estructural (duck typing).
# No se usa issubclass() en importación: el Protocol no es @runtime_checkable.