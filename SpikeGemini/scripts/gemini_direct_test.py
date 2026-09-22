import os

from dotenv import load_dotenv
from google import genai

def main():
    load_dotenv(override=True)

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv(
    "GEMINI_GENERATION_MODEL",
    "gemini-3.6-flash",
    )

    print("API key existe:", bool(api_key))
    print("Modelo:", model)

    client = genai.Client(api_key=api_key)

    response = client.interactions.create(
    model=model,
    input="Explica qué es OCI Object Storage en una frase.",
    )

    print("Respuesta:")
    print(response.output_text)

if __name__ == "__main__":
    main()