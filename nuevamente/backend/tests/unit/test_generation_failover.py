"""Tests para `FailoverLLMProvider` (cadena Cohere → Gemini → mock)."""
import pytest

from src.core.exceptions import LLMProviderError
from src.generation.failover import FailoverLLMProvider


class _Provider:
    """Provider fake que devuelve o falla según configuración."""

    # *******************************************************************
    #  MEJORA AUD-016 — 2026-10-15
    #  Firma partida en varias líneas para respetar el límite de 100
    #  caracteres de `ruff check` (paso de lint del CI).
    # *******************************************************************
    def __init__(
        self,
        name: str,
        response: str | None = None,
        should_fail: bool = False,
        fail_count: int = 0,
    ):
        self.name = name
        self.response = response or f"[{name}] respuesta"
        self.should_fail = should_fail
        self.fail_count = fail_count
        self._attempts = 0

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        if self.should_fail:
            self._attempts += 1
            if self._attempts <= self.fail_count:
                raise RuntimeError(f"{self.name} fallo transitorio #{self._attempts}")
        return self.response


def test_primary_succeeds_no_backup_called():
    """Si el primario tiene éxito, no se llama al respaldo."""
    primary = _Provider("Primary", response="ok")
    backup = _Provider("Backup", response="backup")

    chain = FailoverLLMProvider(primary=primary, backup=backup)
    result = chain.generate("prompt")

    assert result == "ok"


def test_primary_fails_backup_succeeds():
    """Si el primario falla, se usa el respaldo."""
    primary = _Provider("Primary", should_fail=True, fail_count=1)
    backup = _Provider("Backup", response="fallback ok")

    chain = FailoverLLMProvider(primary=primary, backup=backup)
    result = chain.generate("prompt")

    assert result == "fallback ok"


def test_both_fail_raises_error():
        """Si ambos fallan, se propaga el error del segundo."""
        primary = _Provider("Primary", should_fail=True, fail_count=1)
        backup = _Provider("Backup", should_fail=True, fail_count=1)

        chain = FailoverLLMProvider(primary=primary, backup=backup)

        with pytest.raises(LLMProviderError, match="Todos los proveedores LLM fallaron"):
            chain.generate("prompt")


def test_single_provider_no_backup():
    """Si no hay respaldo configurado, falla directo."""
    primary = _Provider("Solo", should_fail=True, fail_count=1)

    chain = FailoverLLMProvider(primary=primary, backup=None)

    with pytest.raises(LLMProviderError, match="Todos los proveedores LLM fallaron"):
        chain.generate("prompt")


def test_primary_transient_failure_then_backup():
    """Fallo transitorio en primario (1 intento), luego respaldo ok."""
    primary = _Provider("Primary", should_fail=True, fail_count=1)
    backup = _Provider("Backup", response="fallback ok")

    chain = FailoverLLMProvider(primary=primary, backup=backup)
    result = chain.generate("prompt")

    assert result == "fallback ok"


def test_logs_warning_on_primary_failure(caplog):
    """Al fallar el primario, se loguea un warning con nombres de ambos."""

    primary = _Provider("CohereLLMProvider", should_fail=True, fail_count=1)
    backup = _Provider("GeminiLLMProvider", response="fallback ok")

    chain = FailoverLLMProvider(primary=primary, backup=backup)

    with caplog.at_level("WARNING"):
        chain.generate("test")

    assert any("llm_primary_failed_fallback_to_backup" in r.message for r in caplog.records)
    assert any("_Provider" in r.message for r in caplog.records)