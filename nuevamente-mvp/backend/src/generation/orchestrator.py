from src.generation.models import GenerationRequest, GeneratedContent
from src.generation.profiles import PROFILES
from src.core.exceptions import LLMProviderError
from src.core.logging import get_logger

log = get_logger(__name__)

PROMPT_TEMPLATE_PATH = "src/generation/prompts/generacion_v1.txt"


class GenerationService:
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider

    def _build_prompt(self, request: GenerationRequest) -> str:
        # BE-GEN-003a — combinar contexto + parámetros pedagógicos
        with open(PROMPT_TEMPLATE_PATH, encoding="utf-8") as f:
            template = f.read()
        return template.format(
            perfil=request.profile,
            formato=request.format,
            nicho=request.niche or "general",
            nivel=request.detail_level,
            contexto=request.context,
        )

    def generate(self, request: GenerationRequest) -> GeneratedContent:
        prompt = self._build_prompt(request)
        try:
            # BE-GEN-003b — invocar LLMProvider (timeout/retry ya viven en el provider)
            content = self.llm_provider.generate_content(prompt)
        except Exception as exc:  # noqa: BLE001
            log.error("generation_failed", error=str(exc))
            raise LLMProviderError("Fallo al generar contenido con el LLM") from exc

        # BE-GEN-003c — la respuesta ya llega mapeada a GeneratedContent via schema
        log.info("content_generated", profile=request.profile, format=request.format)
        return content
