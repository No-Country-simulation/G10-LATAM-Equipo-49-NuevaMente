from typing import Protocol
import json

from tenacity import retry, stop_after_attempt, wait_fixed
from src.core.config import settings
from src.core.exceptions import LLMProviderError
from src.generation.models import GeneratedContent


class LLMProvider(Protocol):
    def generate_content(self, prompt: str) -> GeneratedContent: ...
    def generate_json(self, prompt: str) -> dict: ...


class GeminiLLMProvider:
    def __init__(self, api_key: str, model: str):
        from google import genai

        if not api_key:
            raise LLMProviderError("GEMINI_API_KEY no configurada")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    @retry(stop=stop_after_attempt(settings.LLM_MAX_RETRIES + 1), wait=wait_fixed(1))
    def generate_content(self, prompt: str) -> GeneratedContent:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": GeneratedContent,
                "temperature": 0.3,
            },
        )
        return GeneratedContent.model_validate_json(response.text)

    @retry(stop=stop_after_attempt(settings.LLM_MAX_RETRIES + 1), wait=wait_fixed(1))
    def generate_json(self, prompt: str) -> dict:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"response_mime_type": "application/json", "temperature": 0},
        )
        return json.loads(response.text)


class MockLLMProvider:
    """Determinista, sin red — usado en dev/tests (LLM_PROVIDER=mock)."""

    def generate_content(self, prompt: str) -> GeneratedContent:
        return GeneratedContent(
            titulo="Contenido de prueba",
            cuerpo="Este es un contenido generado por el proveedor mock, "
                   "basado únicamente en el contexto simulado.",
            conceptos_clave=["concepto-a", "concepto-b"],
            prerrequisitos=["ninguno"],
            tiempo_estimado_min=10,
            dificultad="media",
        )

    def generate_json(self, prompt: str) -> dict:
        # Usado por claims_extractor y fidelity_checker en modo mock
        if "responde únicamente con SI, NO o PARCIAL" in prompt.lower():
            return {"verdict": "SI"}
        return {
            "claims": [
                {"id": "claim-1", "text": "Afirmación de ejemplo derivada del contexto"},
                {"id": "claim-2", "text": "Segunda afirmación de ejemplo"},
            ]
        }


def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER == "gemini":
        return GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
    return MockLLMProvider()
