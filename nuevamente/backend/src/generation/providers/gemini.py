"""Implementación de `LLMProvider` con Google Gemini API (free tier), DT-09.

Usa `google-genai` SDK. Reintentos con backoff exponencial y traducción
de errores a `LLMProviderError`.
"""
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
        """Importación perezosa del cliente de google-genai."""
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Genera texto a partir de `prompt` usando Gemini.

        Lanza:
            LLMProviderError: si la llamada falla o agota los reintentos.
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
                    },
                )
                return response.text or ""
            except Exception as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    wait = 2**attempt
                    time.sleep(wait)
                continue

        msg = f"Fallo al generar contenido tras {self._max_retries + 1} intentos: {last_exc}"
        raise LLMProviderError(msg) from last_exc