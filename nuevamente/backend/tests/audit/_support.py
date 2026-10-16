"""Utilidades compartidas por la suite de auditoría (datos controlados, sin red ni credenciales)."""
from pathlib import Path

from src.api.orchestrator import PipelineOrchestrator
from src.api.schemas import AdaptRequest

AUDIT_DIR = Path(__file__).resolve().parent
REPO_ROOT = AUDIT_DIR.parents[2]  # .../nuevamente
DOC_CLOUD = (AUDIT_DIR / "fixtures" / "arquitectura_cloud.md").read_text(encoding="utf-8")

PERFIL = "Principiante / Transición de Carrera"
FORMATO = "Resumen Ejecutivo (TL;DR)"


def ingest_cloud_doc(orchestrator: PipelineOrchestrator | None = None):
    """Ingiere el documento de prueba y devuelve (orquestador, document_id)."""
    orc = orchestrator or PipelineOrchestrator()
    return orc, orc.ingest("arquitectura_cloud.md", DOC_CLOUD.encode("utf-8")).document_id


def adapt(orc: PipelineOrchestrator, document_id: str, **overrides):
    """Ejecuta `run_adaptation` con parámetros válidos por defecto."""
    data = {"document_id": document_id, "perfil": PERFIL, "formato": FORMATO}
    data.update(overrides)
    return orc.run_adaptation(AdaptRequest(**data))
