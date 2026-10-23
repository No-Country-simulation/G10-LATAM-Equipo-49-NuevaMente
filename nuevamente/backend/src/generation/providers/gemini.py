"""Implementación de `LLMProvider` con Google Gemini API (free tier), DT-09.

Usa `google-genai` SDK. Timeout explícito, reintentos con backoff exponencial
SOLO para errores reintentables (429/5xx) y traducción de errores a
`LLMProviderError`. Un texto vacío se trata como fallo (AUD-011).
"""
import re
import time
from typing import Any

from src.core.config import get_settings
from src.core.exceptions import LLMProviderError


class GeminiLLMProvider:
    """Cumple el contrato `LLMProvider` invocando la API de Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model = model or settings.GEMINI_MODEL
        self._timeout = timeout or settings.LLM_TIMEOUT_SECONDS
        self._max_retries = max_retries if max_retries is not None else settings.LLM_MAX_RETRIES
        self._client: Any = None

    def _get_client(self) -> Any:
        """Importación perezosa del cliente de google-genai.

        *********************************************************************
        MEJORA AUD-011d — 2026-10-15
        Igual que en el proveedor de embeddings: `self._timeout` se guardaba
        pero nunca llegaba al SDK, así que una llamada podía colgarse sin
        límite. Ahora se pasa vía `http_options` (milisegundos).
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
        """Solo 429 (cuota) y 5xx (servidor) / timeout son reintentables (AUD-011d).

        Antes se reintentaba cualquier excepción —incluidos errores de
        credenciales— con esperas 1-2-4 s.
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

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Genera texto a partir de `prompt` usando Gemini.

        Lanza:
            LLMProviderError: si la llamada falla, agota los reintentos o la
                respuesta viene vacía (antes se devolvía "" en silencio, AUD-011).
        """
        client = self._get_client()
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": 8192,
                        "response_mime_type": "application/json",
                    },
                )
                texto = response.text or ""
                if texto.strip():
                    return texto
                last_exc = LLMProviderError("La API de Gemini devolvió una respuesta vacía.")
                break
            except Exception as exc:
                last_exc = exc
                if attempt >= self._max_retries or not self._is_retryable(exc):
                    break
                time.sleep(2**attempt)

        msg = f"Fallo al generar contenido tras {self._max_retries + 1} intentos: {last_exc}"
        raise LLMProviderError(msg) from last_exc