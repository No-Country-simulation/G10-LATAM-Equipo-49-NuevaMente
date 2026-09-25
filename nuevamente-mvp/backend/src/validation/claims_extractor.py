from src.validation.models import Claim


def extract_claims(llm_provider, generated_text: str) -> list[Claim]:
    prompt = (
        "Extrae las afirmaciones (claims) verificables del siguiente texto. "
        "Responde en JSON: {\"claims\": [{\"id\": \"claim-1\", \"text\": \"...\"}]}\n\n"
        f"TEXTO:\n{generated_text}"
    )
    result = llm_provider.generate_json(prompt)
    return [Claim(**c) for c in result.get("claims", [])]
