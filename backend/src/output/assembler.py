"""Ensamblador del JSON final (BE-OUT-003, COMP-08)."""
from src.core.config import get_settings
from src.generation.models import ContenidoAdaptado as GeneratedContent
from src.output.schema import (
    AlmacenamientoOCI,
    ContenidoAdaptado,
    EvaluacionCalidad,
    Metadatos,
    NuevaMenteOutput,
    Source,
)
from src.validation.models import FidelityEvaluation


def assemble_output(
    doc_id: str,
    perfil: str,
    formato: str,
    nivel_detalle: str,
    contenido: GeneratedContent | None,
    fidelidad: FidelityEvaluation,
    nicho: str | None = None,
    sources: list[Source] | None = None,
    items: list | None = None,
) -> NuevaMenteOutput:
    """Compone un `NuevaMenteOutput` válido a partir de las salidas de
    Generation (COMP-06) y Validation (COMP-07).

    `status` según el caso:
        - "SUCCESS" si hay contenido y `fidelidad.score >= FIDELITY_THRESHOLD`
        - "PARTIAL" si hay contenido pero el score es bajo o nulo
        - "NO_CONTEXT"/"ERROR" se resuelven en `api/orchestrator.py` y nunca
          llegan aquí con contenido nulo (no se invoca este ensamblador).
    """
    settings = get_settings()

    min_score = settings.FIDELITY_THRESHOLD
    score = fidelidad.score
    status = "SUCCESS" if score is not None and score >= min_score else "PARTIAL"

    contenido_adaptado = None
    if contenido is not None:
        contenido_adaptado = ContenidoAdaptado(
            cuerpo=contenido.cuerpo,
            conceptos_clave=contenido.conceptos_clave,
            prerrequisitos=contenido.prerrequisitos,
            tiempo_estimado_min=contenido.tiempo_estimado_min,
            items=list(items or []),
        )

    return NuevaMenteOutput(
        status=status,
        metadatos=Metadatos(
            doc_id=doc_id,
            perfil=perfil,
            formato=formato,
            nicho=nicho,
            nivel_detalle=nivel_detalle,
            sources=sources or [],
        ),
        contenido_adaptado=contenido_adaptado,
        evaluacion_calidad=EvaluacionCalidad(
            fidelidad_score=score,
            claims_no_soportados=fidelidad.claims_no_soportados,
            dificultad=None,
            observaciones=fidelidad.observaciones,
        ),
        almacenamiento_oci=AlmacenamientoOCI(bucket=""),  # lo completa el caller
    )