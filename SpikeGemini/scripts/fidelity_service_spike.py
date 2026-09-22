from app.services.fidelity_service import FidelityService


def main():

    service = FidelityService()

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
