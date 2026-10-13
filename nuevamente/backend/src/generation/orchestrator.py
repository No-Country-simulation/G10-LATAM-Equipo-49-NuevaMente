"""Orquestador de generación adaptada (BE-GEN-003, GEN-004, GEN-005).

Subtareas implementadas:
    BE-GEN-003a — construir el prompt final combinando contexto + perfil/formato/nicho
    BE-GEN-003b — invocar `LLMProvider.generate(...)` con manejo de timeout/retry
    BE-GEN-003c — mapear la respuesta del LLM a `ContenidoAdaptado`
"""

import json
import re
from typing import Any, Dict

from src.core.exceptions import LLMProviderError
from src.generation.llm_provider import LLMProvider
from src.generation.models import AdaptationRequest, ContenidoAdaptado


SYSTEM_PROMPT = """Eres un experto en pedagogía y adaptación de contenidos técnicos.
Tu tarea es tomar fragmentos de documentación técnica y adaptarlos según los parámetros solicitados.

REGLAS OBLIGATORIAS:
1. Responde ÚNICAMENTE con un objeto JSON válido, sin bloques de código markdown ni texto adicional.
2. Básate estrictamente en el contenido provisto en las fuentes.
3. El formato JSON debe cumplir exactamente con esta estructura:
{
  "titulo": "Título atractivo y adaptado",
  "introduccion_contextualizada": "Introducción personalizada según el perfil y nicho",
  "items": [
    {
      "concepto": "Nombre del concepto o paso",
      "explicacion": "Explicación detallada orientada al formato pedagógico",
      "ejemplo_o_aplicacion": "Ejemplo práctico aplicado al nicho"
    }
  ],
  "conceptos_clave": ["concepto1", "concepto2"],
  "tiempo_estimado_estudio_minutos": 10
}
"""

USER_PROMPT_TEMPLATE = """PARÁMETROS DE ADAPTACIÓN:
- Perfil del usuario: {perfil}
- Formato pedagógico: {formato}
- Nicho industrial: {nicho}

FUENTES / CONTEXTO RECUPERADO DE LA DOCUMENTACIÓN:
{context_text}

Genera la adaptación educativa cumpliendo con el perfil, formato y nicho solicitados.
"""


class GenerationOrchestrator:
    """Implementación del flujo de generación adaptada."""

    def generate_content(
        self,
        request: AdaptationRequest,
        contexto: str,
        provider: LLMProvider,
    ) -> ContenidoAdaptado:
        """Genera contenido adaptado a partir de `contexto` y los
        parámetros de `request`.

        Precondición: `contexto` no vacío (garantizado por `rag.context_builder.build_context`).

        Lanza:
            LLMProviderError: propagada desde `provider.generate(...)` o si falla el parseo JSON.
        """
        # 1. BE-GEN-003a: Construir el prompt unificado
        user_prompt = USER_PROMPT_TEMPLATE.format(
            perfil=request.perfil,
            formato=request.formato,
            nicho=request.nicho,
            context_text=contexto,
        )

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        # 2. BE-GEN-003b: Invocar LLMProvider (reintentos y timeouts ya manejados por el provider)
        raw_response = provider.generate(full_prompt)

        # 3. BE-GEN-003c: Parsear respuesta y mapear a ContenidoAdaptado
        return self._parse_and_map_response(raw_response)

    def _parse_and_map_response(self, raw_response: str) -> ContenidoAdaptado:
        """Limpia el markdown si el LLM incluye triple backticks y convierte la respuesta JSON a ContenidoAdaptado."""
        cleaned_json_str = self._clean_markdown_fences(raw_response)

        try:
            data: Dict[str, Any] = json.loads(cleaned_json_str)

            # Instanciación compatible con Pydantic / dataclass según el modelo interno
            if hasattr(ContenidoAdaptado, "model_validate"):
                return ContenidoAdaptado.model_validate(data)

            return ContenidoAdaptado(**data)

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise LLMProviderError(
                f"La respuesta del LLM no tiene un formato JSON válido para ContenidoAdaptado: {str(e)}"
            ) from e

    @staticmethod
    def _clean_markdown_fences(text: str) -> str:
        """Remueve encuadramientos ```json ... ``` devueltos comúnmente por modelos Gemini."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        return text.strip()