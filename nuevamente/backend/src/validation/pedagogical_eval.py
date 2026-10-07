"""Evaluación pedagógica complementaria (VAL-003, VAL-004).

No forma parte del score de fidelidad (RF-014); alimenta los metadatos
educativos del contrato de salida (RF-015).
"""
from src.generation.profiles import conceptos_clave


def evaluate_pedagogical_metadata(contenido_generado: str) -> dict:
    """Deriva metadata pedagógica adicional del contenido generado."""
    return {
        "conceptos_clave": conceptos_clave(contenido_generado, n=4),
        "prerrequisitos": [],
        "dificultad": "estandar",
    }
