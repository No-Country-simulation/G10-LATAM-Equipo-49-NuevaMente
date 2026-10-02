"""Catálogo declarativo de perfiles y formatos pedagógicos del MVP,
más las plantillas de apertura por perfil (GEN-001, GEN-002, REQ-24).
"""
import re
from collections import Counter

PERFILES_MVP: list[str] = [
    "principiante",
    "developer",
    "lider_tecnico",
    "ejecutivo",
]

FORMATOS_MVP: list[str] = [
    "tutorial",
    "resumen_ejecutivo",
    "flashcards",
    "quiz",
    "guion",
]

# Aperturas contextualizadoras por perfil (de la demo base de Fase 1)
INTROS: dict[str, str] = {
    "principiante": (
        "Imagina este concepto como una caja de herramientas: "
        "empezamos por lo más simple."
    ),
    "developer": "Este concepto se conecta con lo que ya usas en el día a día del desarrollo.",
    "lider_tecnico": "Analicemos el concepto desde el diseño, los trade-offs y la escalabilidad.",
    "ejecutivo": "En una línea: esto impacta costos, riesgos y velocidad de entrega.",
}

# Títulos por formato (de la demo base de Fase 1)
TITULOS: dict[str, str] = {
    "flashcards": "Flashcards de memorización",
    "quiz": "Quiz interactivo",
    "tutorial": "Guía práctica paso a paso",
    "resumen_ejecutivo": "Resumen ejecutivo (TL;DR)",
    "guion": "Guion de clase / video",
}

STOPWORDS: set[str] = {
    "de", "la", "el", "en", "y", "a", "los", "del", "se", "las", "por",
    "un", "una", "que", "con", "para", "su", "es", "son", "o", "como",
    "mas", "entre", "sobre", "este", "esta", "the", "of", "and", "in",
    "to", "is", "are", "it", "that", "this",
}


def conceptos_clave(texto: str, n: int = 4) -> list[str]:
    """Extrae los `n` términos más frecuentes excluyendo stopwords."""
    freq = Counter(w for w in re.findall(r"[A-Za-zÁ-ú]{4,}", texto.lower()) if w not in STOPWORDS)
    return [w for w, _ in freq.most_common(n)] or ["concepto"]