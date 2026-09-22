import json

from app.providers.gemini_provider import GeminiProvider


class FidelityService:

    def __init__(self, provider: GeminiProvider | None = None):
        self.provider = provider or GeminiProvider()

    def evaluate_claim(
        self,
        context: str,
        claim: str,
    ) -> dict:

        if not context.strip():
            raise ValueError("El contexto no puede estar vacío.")

        if not claim.strip():
            raise ValueError("El claim no puede estar vacío.")

        prompt = f"""
Eres un evaluador de fidelidad documental.

Determina si el siguiente claim está respaldado
por el contexto proporcionado.

Contexto:
{context}

Claim:
{claim}

Devuelve ÚNICAMENTE un JSON válido con esta estructura:

{{
    "supported": true,
    "confidence": 1.0,
    "reason": "explicación breve"
}}

Reglas:

- "supported" debe ser true si el contexto respalda el claim.
- "supported" debe ser false si el contexto no respalda el claim.
- "confidence" debe ser un número entre 0.0 y 1.0.
- "reason" debe explicar brevemente la decisión.
- No agregues Markdown.
- No agregues texto fuera del JSON.
"""

        response = self.provider.generate(prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Gemini no devolvió JSON válido: {response}"
            ) from exc

        self._validate_result(result)

        return result

    @staticmethod
    def _validate_result(result: dict) -> None:

        required_fields = {
            "supported",
            "confidence",
            "reason",
        }

        missing = required_fields - result.keys()

        if missing:
            raise ValueError(
                f"Faltan campos en la respuesta: {missing}"
            )

        if not isinstance(result["supported"], bool):
            raise ValueError(
                "'supported' debe ser booleano."
            )

        if not isinstance(result["confidence"], (int, float)):
            raise ValueError(
                "'confidence' debe ser numérico."
            )

        if not 0.0 <= result["confidence"] <= 1.0:
            raise ValueError(
                "'confidence' debe estar entre 0.0 y 1.0."
            )

        if not isinstance(result["reason"], str):
            raise ValueError(
                "'reason' debe ser texto."
            )
