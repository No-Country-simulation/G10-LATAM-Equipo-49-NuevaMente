from app.services.fidelity_service_threshold import FidelityService1


class FakeGeminiProvider:

    def __init__(self, response):
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response


def run_test(name, response):

    print(f"\n--- {name} ---")

    provider = FakeGeminiProvider(response)

    service = FidelityService1(
        provider=provider
    )

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

    print(f"Supported: {result['supported']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Threshold: {result['threshold']}")
    print(f"Passed: {result['passed']}")
    print(f"Reason: {result['reason']}")


def main():

    run_test(
        "Caso 1 - Claim respaldado",
        """
        {
            "supported": true,
            "confidence": 0.95,
            "reason": "El contexto respalda directamente el claim."
        }
        """,
    )

    run_test(
        "Caso 2 - Confianza insuficiente",
        """
        {
            "supported": true,
            "confidence": 0.70,
            "reason": "Existe cierta evidencia, pero no es suficiente."
        }
        """,
    )

    run_test(
        "Caso 3 - Claim no respaldado",
        """
        {
            "supported": false,
            "confidence": 1.0,
            "reason": "El contexto no respalda el claim."
        }
        """,
    )


if __name__ == "__main__":
    main()
