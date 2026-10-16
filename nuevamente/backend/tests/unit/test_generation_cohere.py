"""Tests para `CohereLLMProvider` (BE-GEN-003).

Usa un cliente Cohere v2 inyectado (fake) para validar el comportamiento
sin necesidad de credenciales reales ni red.
"""
import pytest

# *****************************************************************************
#  MEJORA AUD-016 — 2026-10-15
#  Se parten las cadenas JSON largas (antes en una sola línea) para respetar la
#  longitud máxima de 100 caracteres que exige `ruff check`, de modo que el
#  paso de lint del CI quede limpio.
# *****************************************************************************
_JSON_HOLA = (
    '{"cuerpo": "hola", "conceptos_clave": ["a"], "prerrequisitos": [],'
    ' "tiempo_estimado_min": 5}'
)
_JSON_OK = (
    '{"cuerpo": "ok", "conceptos_clave": [], "prerrequisitos": [],'
    ' "tiempo_estimado_min": 1}'
)


class _FakeCohereClient:
    """Cliente Cohere v2 falso que devuelve respuestas JSON válidas."""

    def __init__(
        self,
        content: str | None = (
            '{"cuerpo": "texto generado", "conceptos_clave": ["a"],'
            ' "prerrequisitos": [], "tiempo_estimado_min": 10}'
        ),
    ):
        self.content = content
        self.calls = []

    def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        response_format: dict,
        max_tokens: int,
    ):
        self.calls.append({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "response_format": response_format,
            "max_tokens": max_tokens,
        })
        # Simular respuesta v2: message.content[0].text
        ContentBlock = type("ContentBlock", (), {"text": self.content})
        Message = type("Message", (), {"content": [ContentBlock()]})
        ChatResponse = type("ChatResponse", (), {"message": Message()})
        return ChatResponse()


class _FailingCohereClient:
    """Cliente que siempre falla."""

    def chat(self, *args, **kwargs):
        raise RuntimeError("Cohere API caído")


class _EmptyContentClient:
    """Cliente que devuelve contenido vacío."""

    def chat(self, *args, **kwargs):
        return type(
            "ChatResponse",
            (),
            {"message": type("Message", (), {"content": []})()},
        )()


def _make_provider(client, max_retries: int = 1):
    """Crea un CohereLLMProvider inyectando un cliente fake."""
    from src.generation.providers.cohere import CohereLLMProvider

    provider = CohereLLMProvider.__new__(CohereLLMProvider)
    provider._client = client
    provider._model = "command-r-plus"
    provider._max_retries = 1
    provider._max_tokens = 4096
    return provider


def test_generate_returns_json_text():
    """`generate` devuelve el texto JSON del primer bloque de contenido."""
    client = _FakeCohereClient(_JSON_HOLA)
    provider = _make_provider(client)

    result = provider.generate("prompt de prueba", temperature=0.2)

    assert result == _JSON_HOLA


def test_generate_passes_correct_parameters():
    """Pasa model, messages, temperature, response_format y max_tokens correctos."""
    client = _FakeCohereClient()
    provider = _make_provider(client)

    provider.generate("hola mundo", temperature=0.5)

    call = client.calls[0]
    assert call["model"] == "command-r-plus"
    assert call["temperature"] == 0.5
    assert call["response_format"] == {"type": "json_object"}
    assert call["max_tokens"] == 4096
    assert call["messages"] == [{"role": "user", "content": "hola mundo"}]


def test_generate_passes_temperature():
    """Pasa la temperatura correctamente."""
    client = _FakeCohereClient()
    provider = _make_provider(client)

    provider.generate("hola", temperature=0.7)

    assert client.calls[0]["temperature"] == 0.7


def test_generate_handles_empty_content():
    """Si `content` está vacío o None, lanza LLMProviderError."""
    client = _EmptyContentClient()
    provider = _make_provider(client)

    with pytest.raises(Exception, match="sin contenido de texto válido"):
        provider.generate("hola")


def test_generate_retries_on_failure():
    """Reintenta con backoff exponencial ante fallo transitorio."""
    attempts = {"count": 0}

    class _FlakyClient:
        def chat(self, *args, **kwargs):
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise RuntimeError("transient error")
            return type(
                "ChatResponse",
                (),
                {
                    "message": type(
                        "Message",
                        (),
                        {"content": [type("C", (), {"text": _JSON_OK})()]},
                    ),
                },
            )()

    client = _FlakyClient()
    provider = _make_provider(client)

    result = provider.generate("hola")
    assert result == _JSON_OK
    assert attempts["count"] == 2


def test_generate_fails_after_max_retries():
    """Tras agotar reintentos, propaga LLMProviderError."""
    client = type(
        "AlwaysFailClient",
        (),
        {"chat": lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("API down"))},
    )()
    provider = _make_provider(client)

    with pytest.raises(Exception, match="Fallo al generar contenido"):
        provider.generate("hola")


def test_generate_handles_missing_content_attribute():
    """Si response.message.content es None, lanza error."""
    class _NoneContentClient:
        def chat(self, *args, **kwargs):
            return type("Resp", (), {"message": type("Msg", (), {"content": None})()})()

    client = _NoneContentClient()
    provider = _make_provider(client)

    with pytest.raises(Exception, match="sin contenido de texto válido"):
        provider.generate("hola")