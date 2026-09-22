import os
from dotenv import load_dotenv
from google import genai

# Cargar variables del archivo .env
load_dotenv()

# Obtener API Key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")

# Crear cliente
client = genai.Client(api_key=api_key)

# Primera llamada a Gemini
interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Responde solamente: Gemini funciona."
)

print(interaction.output_text)