from app.providers.gemini_provider import GeminiProvider


def main():
    provider = GeminiProvider()

    response = provider.generate(
        "Responde solamente: Gemini funciona."
    )

    print("Respuesta de Gemini:")
    print(response)


if __name__ == "__main__":
    main()
