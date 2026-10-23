"""Implementación de `EmbeddingProvider` con Google Gemini API (free tier), DT-09.

Usa `google-genai` SDK. Llamadas en lotes de 100 (límite de la API),
reintentos con backoff exponencial SOLO para errores reintentables
(429 y 5xx), timeout explícito y vectores optimizados para recuperación
(`task_type` + `output_dimensionality`). Los errores se traducen a
`LLMProviderError` (502) para que `embed_chunks` los propague sin
degradarlos (cumple OUT-004 / AUD-022).
"""
import re
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
        self._dimensions = settings.active_embedding_dimensions
        self._client: Any = None

    def _get_client(self) -> Any:
        """Importación perezosa del cliente de google-genai forzando la API v1.

        *********************************************************************
        MEJORA AUD-011b — 2026-10-15
        Antes `self._timeout` se guardaba pero nunca llegaba al SDK y todas las
        llamadas podían colgarse indefinidamente. Ahora el timeout configurado
        se pasa vía `http_options` (en milisegundos, como espera el SDK).
        *********************************************************************
        """
        if self._client is None:
            from google import genai

            self._client = genai.Client(
                api_key=self._api_key,
                http_options={"api_version": "v1", "timeout": self._timeout * 1000},
            )
        return self._client

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        """Solo 429 (cuota) y 5xx (servidor) son reintentables.

        *********************************************************************
        MEJORA AUD-011a — 2026-10-15
        Antes se reintentaba CUALQUIER excepción (p. ej. un 403 de credenciales
        inválidas) con esperas 1-2-4 s, bloqueando el hilo inútilmente. Ahora
        los errores de autenticación/entrada fallan de inmediato.
        *********************************************************************
        """
        status = getattr(exc, "status_code", None)
        if status is None:
            status = getattr(exc, "code", None)
        if isinstance(status, int):
            return status == 429 or 500 <= status < 600
        if isinstance(status, str):
            upper = status.upper()
            if any(tag in upper for tag in ("RESOURCE_EXHAUSTED", "UNAVAILABLE", "INTERNAL")):
                return True
            if any(
                tag in upper
                for tag in ("PERMISSION_DENIED", "UNAUTHENTICATED", "INVALID_ARGUMENT", "NOT_FOUND")
            ):
                return False
        if isinstance(exc, (TimeoutError, ConnectionError)):
            return True
        return bool(re.search(r"\b(429|5\d{2})\b", str(exc)))

    def _embed_with_retry(self, texts: list[str], task_type: str) -> list[list[float]]:
        """Genera embeddings con reintentos selectivos y backoff exponencial.

        *********************************************************************
        MEJORA AUD-011c — 2026-10-15
        Antes `embed_content` se llamaba sin `config`, por lo que la API no
        recibía `task_type` (vectores no optimizados para recuperación) ni
        dimensiones. Ahora se declaran ambos.
        *********************************************************************
        """
        client = self._get_client()
        last_exc: Exception | None = None

        # Sanear el nombre del modelo quitando 'models/' si viene en el entorno.
        model_name = self._model.replace("models/", "") if self._model else "gemini-embedding-2"

        config: dict[str, Any] = {"task_type": task_type}
        if "embedding" in model_name:
            config["output_dimensionality"] = self._dimensions

        for attempt in range(self._max_retries + 1):
            try:
                response = client.models.embed_content(
                    model=model_name,
                    contents=texts,
                    config=config,
                )
                # La API devuelve una lista de ContentEmbedding con .values
                return [emb.values for emb in response.embeddings]
            except Exception as exc:
                last_exc = exc
                if attempt >= self._max_retries or not self._is_retryable(exc):
                    break
                time.sleep(2**attempt)

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
            embeddings = self._embed_with_retry(batch, task_type="RETRIEVAL_DOCUMENT")
            all_embeddings.extend(embeddings)

        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        """Genera el vector de una consulta individual (para retrieval)."""
        return self._embed_with_retry([text], task_type="RETRIEVAL_QUERY")[0]


# Nota: cumple el Protocol correspondiente por forma estructural (duck typing).
# No se usa issubclass() en importación: el Protocol no es @runtime_checkable.
