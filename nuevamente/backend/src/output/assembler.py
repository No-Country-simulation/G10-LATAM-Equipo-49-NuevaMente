"""Ensamblador del JSON final (BE-OUT-003, COMP-08)."""
from src.generation.models import ContenidoAdaptado as GeneratedContent
from src.generation.profiles import FormatoSalida, NichoSector, PerfilDestinatario
from src.output.schema import NuevaMenteOutput
from src.validation.models import FidelityEvaluation


def assemble_output(
    doc_id: str,
    perfil: PerfilDestinatario,
    formato: FormatoSalida,
    contenido: GeneratedContent | None,
    fidelidad: FidelityEvaluation,
    nicho: NichoSector = "General",
) -> NuevaMenteOutput:
    """Compone un `NuevaMenteOutput` válido a partir de las salidas de
    Generation (COMP-06) y Validation (COMP-07).

    Determina `status` según el caso:
        - "SUCCESS" si hay contenido y `fidelidad.score >= FIDELITY_THRESHOLD`
        - "PARTIAL" si hay contenido pero el score es bajo o nulo
        - "NO_CONTEXT" si no hubo contexto suficiente (ver `rag.context_builder`)
        - "ERROR" ante fallos no recuperables

    Implementación futura.
    """
    ...