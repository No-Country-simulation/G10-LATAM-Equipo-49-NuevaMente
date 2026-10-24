"""Implementación de `LLMProvider` con Cohere API v2 (DT-09).

Usa `cohere` SDK v2. Llamadas con `response_format={"type": "json_object"}` para
forzar salida JSON estructurada, reintentos con backoff exponencial, y
traducción de errores a `LLMProviderError` para que la API marque el job
como fallido en lugar de presentar una respuesta mock.

El modelo por defecto es `command-r-plus` (alias que apunta a la última
revisión estable). Longitud máxima de salida: `COHERE_MAX_TOKENS` (por
defecto 4096, límite del modelo command-r-plus).

CAMBIO H-08 INICIO — 2026-10-24
La respuesta se valida contra el schema de contenido antes de salir del provider.
CAMBIO H-08 FIN — 2026-10-24
"""
import time
from typing import Any

from pydantic import ValidationError

from src.core.config import get_settings
from src.core.exceptions import LLMProviderError
from src.generation.models import ContenidoAdaptado
from src.generation.prompt_loader import strip_markdown_fences


class CohereLLMProvider:
    """Cumple el contrato `LLMProvider` invocando la API de Cohere v2."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.COHERE_API_KEY
        self._model = model or settings.COHERE_MODEL
        self._timeout = timeout or settings.LLM_TIMEOUT_SECONDS
        self._max_retries = (
            max_retries if max_retries is not None else settings.LLM_MAX_RETRIES
        )
        self._max_tokens = getattr(settings, "COHERE_MAX_TOKENS", 4096)
        self._client: Any = None

    def _get_client(self) -> Any:
        """Importación perezosa del cliente de Cohere v2."""
        if self._client is None:
            import cohere

            self._client = cohere.ClientV2(api_key=self._api_key)
        return self._client

    def _chat_with_retry(self, prompt: str, temperature: float) -> str:
        """Genera texto con reintentos y backoff exponencial."""
        client = self._get_client()
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = client.chat(
                    model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    response_format={"type": "json_object"},
                    max_tokens=self._max_tokens,
                )
                # La respuesta v2 tiene content como lista de bloques; tomamos el primer texto
                content = getattr(response, "message", None)
                if content is not None:
                    content_list = getattr(content, "content", None)
                    if content_list and len(content_list) > 0:
                        first = content_list[0]
                        text = getattr(first, "text", None)
                        if text:
                            # CAMBIO H-08 INICIO — 2026-10-24
                            try:
                                ContenidoAdaptado.model_validate_json(
                                    strip_markdown_fences(text)
                                )
                            except (ValidationError, ValueError) as exc:
                                raise LLMProviderError(
                                    "Respuesta de Cohere inválida: se esperaba JSON "
                                    "con los campos de GeneratedContent."
                                ) from exc
                            return text
                            # CAMBIO H-08 FIN — 2026-10-24
                raise LLMProviderError("Respuesta de Cohere sin contenido de texto válido")
            except Exception as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    wait = 2**attempt
                    time.sleep(wait)
                continue

        msg = f"Fallo al generar contenido tras {self._max_retries + 1} intentos: {last_exc}"
        raise LLMProviderError(msg) from last_exc

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Genera texto a partir de `prompt` usando Cohere.

        Lanza:
            LLMProviderError: si la llamada falla o agota los reintentos.
        """
        return self._chat_with_retry(prompt, temperature)


# Nota: cumple el Protocol correspondiente por forma estructural (duck typing).
# No se usa issubclass() en importación: el Protocol no es @runtime_checkable.