from app.providers.gemini_provider import GeminiProvider


def main():
    provider = GeminiProvider()

    context = """
    OCI Object Storage permite almacenar objetos como documentos,
    imágenes y otros archivos en la nube.
    """

    prompt = f"""
    Contexto:
    {context}

    Explica este concepto para un principiante.
    """

    response = provider.generate(prompt)

    print(response)


if __name__ == "__main__":
    main()