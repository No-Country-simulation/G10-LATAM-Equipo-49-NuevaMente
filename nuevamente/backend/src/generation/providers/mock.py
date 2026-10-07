"""`LLMProvider` en modo mock — determinista y sin red.

Permite desarrollar y probar el pipeline completo sin credenciales.
Devuelve un marcador reconocible para distinguir respuestas mock de reales.
"""


class MockLLMProvider:
    """Cumple el contrato `LLMProvider` sin llamar a ningún servicio externo."""

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Devuelve un marcador determinista que incluye info del prompt."""
        preview = prompt[:120].replace("\n", " ")
        return f"[MOCK-LLM temp={temperature}] {preview}..."