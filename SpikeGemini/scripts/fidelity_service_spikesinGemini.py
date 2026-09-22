from app.services.fidelity_service import FidelityService


class FakeGeminiProvider:

    def generate(self, prompt: str) -> str:
        return """
{
    "supported": true,
    "confidence": 0.95,
    "reason": "El contexto respalda directamente el claim."
}
"""


def main():

    provider = FakeGeminiProvider()

    service = FidelityService(provider=provider)

    context = """
    OCI Object Storage permite almacenar objetos como documentos,
    imágenes y otros archivos en la nube.
    """

    claim = """
    OCI Object Storage almacena objetos.
    """

    result = service.evaluate_claim(
        context=context,
        claim=claim,
    )

    print("Resultado de fidelidad:")
    print(f"Supported: {result['supported']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reason: {result['reason']}")


if __name__ == "__main__":
    main()
