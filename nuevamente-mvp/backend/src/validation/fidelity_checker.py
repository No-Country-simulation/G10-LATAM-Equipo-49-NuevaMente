from src.validation.models import Claim, ClaimEvaluation, FidelityEvaluation
from src.validation.claims_extractor import extract_claims
from src.core.logging import get_logger

log = get_logger(__name__)

WEIGHTS = {"SI": 1.0, "PARCIAL": 0.5, "NO": 0.0}
VALID_VERDICTS = {"SI", "NO", "PARCIAL"}


def _verify_claim(llm_provider, claim: Claim, context: str) -> str:
    prompt = (
        "Eres un verificador estricto. Responde únicamente con SI, NO o PARCIAL, "
        "sin explicación adicional.\n\n"
        f"CLAIM: {claim.text}\n\nCONTEXTO FUENTE:\n{context}"
    )
    try:
        result = llm_provider.generate_json(prompt)
        verdict = str(result.get("verdict", "PARCIAL")).upper()
        return verdict if verdict in VALID_VERDICTS else "PARCIAL"
    except Exception as exc:  # noqa: BLE001  — VAL-005, fallo del LLM-juez
        log.warning("judge_failed_for_claim", claim_id=claim.id, error=str(exc))
        return "EXCLUDED"


def validate_fidelity(llm_provider, generated_text: str, context: str) -> FidelityEvaluation:
    try:
        claims = extract_claims(llm_provider, generated_text)  # BE-VAL-002a
    except Exception as exc:  # noqa: BLE001
        log.error("claim_extraction_failed", error=str(exc))
        return FidelityEvaluation(
            score=None, claims=[], claims_no_soportados=[],
            observaciones=["No fue posible extraer claims: fallo del LLM."],
        )

    if not claims:
        return FidelityEvaluation(score=None, claims=[], claims_no_soportados=[],
                                   observaciones=["No se identificaron claims verificables."])

    evaluations: list[ClaimEvaluation] = []
    observations: list[str] = []
    excluded = 0

    for claim in claims:
        verdict = _verify_claim(llm_provider, claim, context)  # BE-VAL-002b
        if verdict == "EXCLUDED":
            excluded += 1
            observations.append(f"Claim '{claim.id}' excluido del score por fallo del verificador.")
            continue
        evaluations.append(ClaimEvaluation(claim_id=claim.id, claim_text=claim.text, verdict=verdict))

    considered = [e for e in evaluations]  # BE-VAL-002c — agregación determinista
    if not considered:
        return FidelityEvaluation(score=None, claims=evaluations, claims_no_soportados=[],
                                   observaciones=observations or ["Ningún claim pudo evaluarse."])

    score = round(sum(WEIGHTS[e.verdict] for e in considered) / len(considered), 4)
    no_soportados = [e.claim_text for e in considered if e.verdict == "NO"]

    if excluded:
        observations.append(f"{excluded} claim(s) excluidos del cálculo de fidelidad.")

    return FidelityEvaluation(
        score=score, claims=evaluations,
        claims_no_soportados=no_soportados, observaciones=observations,
    )
