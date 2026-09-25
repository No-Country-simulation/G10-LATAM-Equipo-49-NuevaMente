from datetime import datetime, timezone

from src.output.schema import (
    NuevaMenteOutput, Metadata, Source, GeneratedContentOut,
    QualityEvaluation, OCIStorage,
)
from src.generation.models import GeneratedContent
from src.validation.models import FidelityEvaluation
from src.core.config import settings


def assemble_output(
    doc_id: str, profile: str, format_: str, niche: str | None, detail_level: str,
    sources: list[dict], content: GeneratedContent | None,
    fidelity: FidelityEvaluation | None, extra_observations: list[str] | None = None,
) -> NuevaMenteOutput:

    status = "SUCCESS"
    if content is None:
        status = "NO_CONTEXT"
    elif fidelity and fidelity.score is not None and fidelity.score < settings.FIDELITY_THRESHOLD:
        status = "PARTIAL"

    observations = list(extra_observations or [])
    if fidelity:
        observations.extend(fidelity.observaciones)

    return NuevaMenteOutput(
        status=status,
        metadatos=Metadata(
            doc_id=doc_id, profile=profile, format=format_, niche=niche,
            detail_level=detail_level,
            sources=[Source(**s) for s in sources],
        ),
        contenido_adaptado=(
            GeneratedContentOut(**content.model_dump()) if content else None
        ),
        evaluacion_calidad=QualityEvaluation(
            fidelity_score=fidelity.score if fidelity else None,
            claims_no_soportados=fidelity.claims_no_soportados if fidelity else [],
            observaciones=observations,
        ),
        almacenamiento_oci=OCIStorage(bucket=settings.OCI_BUCKET_NAME),
    )
