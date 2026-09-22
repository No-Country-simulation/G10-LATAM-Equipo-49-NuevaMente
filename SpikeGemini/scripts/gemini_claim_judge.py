import json

from app.providers.gemini_provider import GeminiProvider


def main():
    provider = GeminiProvider()

    context = """
    OCI Object Storage permite almacenar objetos como documentos,
    imágenes y otros archivos en la nube.
    """

    #claim = """
    #OCI Object Storage almacena objetos.
    #"""
    claim = """
    OCI Object Storage es un servicio gratuito.
    """
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
- "reason" debe explicar brevemente por qué.
- No agregues Markdown.
- No agregues texto fuera del JSON.
"""

    response = provider.generate(prompt)

    print("Respuesta de Gemini:")
    print(response)

    try:
        result = json.loads(response)

        print("\nResultado procesado:")
        print("Supported:", result["supported"])
        print("Confidence:", result["confidence"])
        print("Reason:", result["reason"])

    except json.JSONDecodeError:
        print("\nERROR: Gemini no devolvió JSON válido.")


if __name__ == "__main__":
    main()