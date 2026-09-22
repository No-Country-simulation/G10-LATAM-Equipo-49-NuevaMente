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

    #claim = """
    #OCI Object Storage es un servicio gratuito e ilimitado que nunca
    #cobra por almacenar archivos.
    # """
    
    claim = """
    OCI Object Storage almacena objetos.
    """
    #prompt = f"""
    #Eres un evaluador de fidelidad documental.

    #Determina si el siguiente claim está respaldado
    #por el contexto proporcionado.

    #Contexto:
    #{context}

    #Claim:
    #{claim}

    #Responde únicamente:
    #SI
    #o
    #NO
    #"""

    #response = provider.generate(prompt)

    prompt = f"""
    Eres un evaluador de fidelidad documental.

    Determina si el siguiente claim está respaldado
    por el contexto proporcionado.

    Contexto:
    {context}

    Claim:
    {claim}

    Responde exclusivamente con un objeto JSON válido,
    sin markdown y sin texto adicional.

    El JSON debe tener exactamente estos campos:

    {{
        "supported": true o false,
        "confidence": número entre 0 y 1,
        "reason": "explicación breve"
    }}

    Reglas:

    - "supported" debe ser true solamente si el contexto respalda
    directamente el claim.
    - "supported" debe ser false si el contexto no proporciona
    evidencia suficiente.
    - "confidence" representa qué tan seguro estás de la decisión.
    - "reason" debe explicar brevemente por qué el claim está o no
      respaldado.
    """

    response = provider.generate(prompt)
    print("Respuesta de Gemini:")
    print(response)
 

if __name__ == "__main__":
    main()