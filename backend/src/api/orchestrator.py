"""Orquestador del pipeline completo (INT-001, INT-002, INT-003, COMP-11).

Responsabilidad: coordinar, EN ORDEN, las llamadas a los servicios de cada
capa (COMP-01 → COMP-09) para resolver una solicitud `POST /adapt`. Este
módulo NO contiene la lógica de cada paso (vive en cada Service); solo
declara el punto único de coordinación, para que `api/main.py` no acumule
lógica de negocio (Fase 5, COMP-11, "Riesgos").
"""
from src.api.schemas import AdaptRequest
from src.output.schema import NuevaMenteOutput


class PipelineOrchestrator:
    """Implementación futura del flujo CU-001 / CU-002 completo."""

    def run_adaptation(self, request: AdaptRequest) -> NuevaMenteOutput:
        """Ejecuta, en orden: retrieval (COMP-05) → generación (COMP-06) →
        validación (COMP-07) → ensamblado de salida (COMP-08) → persistencia
        en OCI (COMP-09).

        Lanza:
            DocumentNotFoundError: si `request.document_id` no existe.
            NoContextError: si el retrieval no encuentra contexto suficiente
                (se traduce a `status=NO_CONTEXT`, no se propaga como 500).

        Implementación futura.
        """
        ...
