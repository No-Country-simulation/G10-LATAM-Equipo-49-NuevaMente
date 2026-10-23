"""Ensamblador del JSON final (BE-OUT-003, COMP-08)."""
from src.core.config import get_settings
from src.generation.models import ContenidoAdaptado as GeneratedContent
from src.generation.profiles import FormatoSalida, NichoSector, PerfilDestinatario
from src.output.schema import (
    EvaluacionCalidad,
    Metadatos,
    NuevaMenteOutput,
    Source,
)
from src.validation.models import FidelityEvaluation

# *****************************************************************************
#  MEJORA AUD-002 / AUD-020 — 2026-10-15
#  `assemble_output` era un *stub* (`...`): el orquestador armaba el JSON a mano
#  y `FIDELITY_THRESHOLD` no se usaba, de modo que `status` nunca se decidía de
#  forma centralizada. Ahora compone el `NuevaMenteOutput` y determina:
#      - "NO_CONTEXT" si no hubo contenido (regla RF-009);
#      - "PARTIAL" si el contenido es mock/degradado o el score es bajo/nulo;
#      - "SUCCESS" si hay contenido real con score >= FIDELITY_THRESHOLD.
# *****************************************************************************
NO_CONTEXT_OBSERVATION = (
    "Sin contexto suficiente en el documento para la solicitud (regla NO_CONTEXT)."
)


def assemble_output(
    doc_id: str,
    perfil: PerfilDestinatario,
    formato: FormatoSalida,
    contenido: GeneratedContent | None,
    fidelidad: FidelityEvaluation,
    nicho: NichoSector = "General",
    sources: list[Source] | None = None,
    es_mock: bool = False,
) -> NuevaMenteOutput:
    """Compone un `NuevaMenteOutput` válido a partir de las salidas de
    Generation (COMP-06) y Validation (COMP-07).

    Determina `status` según el caso:
        - "NO_CONTEXT" si no hubo contenido suficiente (contexto vacío);
        - "PARTIAL" si el contenido es mock/degradado o el score es bajo o nulo;
        - "SUCCESS" si hay contenido real con `fidelidad.score >= FIDELITY_THRESHOLD`.
    """
    metadatos = Metadatos(
        doc_id=doc_id,
        perfil=perfil,
        formato=formato,
        nicho=nicho,
        sources=sources or [],
    )
    observaciones = list(fidelidad.observaciones)

    if contenido is None:
        if NO_CONTEXT_OBSERVATION not in observaciones:
            observaciones.append(NO_CONTEXT_OBSERVATION)
        return NuevaMenteOutput(
            status="NO_CONTEXT",
            metadatos=metadatos,
            contenido_adaptado=None,
            evaluacion_calidad=EvaluacionCalidad(
                fidelidad_score=None,
                claims_no_soportados=[],
                observaciones=observaciones,
            ),
        )

    score = fidelidad.score
    if es_mock:
        status = "PARTIAL"
    elif score is not None and score >= get_settings().FIDELITY_THRESHOLD:
        status = "SUCCESS"
    else:
        status = "PARTIAL"

    return NuevaMenteOutput(
        status=status,
        metadatos=metadatos,
        contenido_adaptado=contenido,
        evaluacion_calidad=EvaluacionCalidad(
            fidelidad_score=score,
            claims_no_soportados=list(fidelidad.claims_no_soportados),
            observaciones=observaciones,
        ),
    )
