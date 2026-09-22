from google import genai

from app.config import settings
from app.providers.interfaces import (
    LLMProvider,
    EmbeddingProvider,
)


class GeminiProvider(LLMProvider):

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        api_key = api_key or settings.GEMINI_API_KEY

        if not api_key:
            raise ValueError(
                "No se encontró GEMINI_API_KEY."
            )

        self.client = genai.Client(api_key=api_key)

        self.model = (
            model
            or settings.GEMINI_GENERATION_MODEL
        )

    def generate(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
    ) -> str:

        if not prompt.strip():
            raise ValueError(
                "El prompt no puede estar vacío."
            )

        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=prompt,
            )

            return interaction.output_text

        except Exception as exc:
            raise RuntimeError(
                f"Error al generar respuesta con Gemini: {exc}"
            ) from exc





from google import genai

from app.config import settings
from app.providers.interfaces import (
    LLMProvider,
    EmbeddingProvider,
)

