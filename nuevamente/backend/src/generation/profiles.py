"""Catálogo declarativo de opciones de adaptación según la propuesta ONE G10.

Contiene los valores que la API valida (`PerfilDestinatario`, `FormatoSalida`,
`NichoSector`) y el contenido de la demo asociada a cada opción: las aperturas
contextualizadoras por perfil (`INTROS`) y los títulos por formato (`TITULOS`).

Las claves de `INTROS` y `TITULOS` son exactamente los valores de
`PERFILES_MVP` y `FORMATOS_MVP`, para que la generación pueda indexar
directamente por el valor que llega en la solicitud.
"""
import re
from collections import Counter
from typing import Literal

PerfilDestinatario = Literal[
    "Principiante / Transición de Carrera",
    "Desarrollador Junior / Semi Senior",
    "Líder Técnico / Arquitecto",
    "Gestor / Ejecutivo (No Técnico)",
]

FormatoSalida = Literal[
    "Guía Práctica Paso a Paso (Tutorial)",
    "Flashcards de Memorización",
    "Quiz Interactivo con Justificaciones",
    "Resumen Ejecutivo (TL;DR)",
    "Guion de Clase / Video",
]

NichoSector = Literal["Fintech", "Salud", "E-commerce", "General"]

PERFILES_MVP: list[PerfilDestinatario] = [
    "Principiante / Transición de Carrera",
    "Desarrollador Junior / Semi Senior",
    "Líder Técnico / Arquitecto",
    "Gestor / Ejecutivo (No Técnico)",
]

FORMATOS_MVP: list[FormatoSalida] = [
    "Guía Práctica Paso a Paso (Tutorial)",
    "Flashcards de Memorización",
    "Quiz Interactivo con Justificaciones",
    "Resumen Ejecutivo (TL;DR)",
    "Guion de Clase / Video",
]

NICHOS_MVP: list[NichoSector] = ["Fintech", "Salud", "E-commerce", "General"]

# Aperturas contextualizadoras por perfil (demo base de Fase 1). La clave es el
# valor exacto de `PerfilDestinatario`.
INTROS: dict[PerfilDestinatario, str] = {
    "Principiante / Transición de Carrera": (
        "Imagina este concepto como una caja de herramientas: "
        "empezamos por lo más simple."
    ),
    "Desarrollador Junior / Semi Senior": (
        "Este concepto se conecta con lo que ya usas en el día a día del desarrollo."
    ),
    "Líder Técnico / Arquitecto": (
        "Analicemos el concepto desde el diseño, los trade-offs y la escalabilidad."
    ),
    "Gestor / Ejecutivo (No Técnico)": (
        "En una línea: esto impacta costos, riesgos y velocidad de entrega."
    ),
}

# Títulos por formato (demo base de Fase 1). La clave es el valor exacto de
# `FormatoSalida`.
TITULOS: dict[FormatoSalida, str] = {
    "Guía Práctica Paso a Paso (Tutorial)": "Guía práctica paso a paso",
    "Flashcards de Memorización": "Flashcards de memorización",
    "Quiz Interactivo con Justificaciones": "Quiz interactivo",
    "Resumen Ejecutivo (TL;DR)": "Resumen ejecutivo (TL;DR)",
    "Guion de Clase / Video": "Guion de clase / video",
}

STOPWORDS: set[str] = {
    "de", "la", "el", "en", "y", "a", "los", "del", "se", "las", "por",
    "un", "una", "que", "con", "para", "su", "es", "son", "o", "como",
    "mas", "entre", "sobre", "este", "esta", "the", "of", "and", "in",
    "to", "is", "are", "it", "that", "this",
}


def conceptos_clave(texto: str, n: int = 4) -> list[str]:
    """Extrae los `n` términos más frecuentes de `texto`, excluyendo stopwords.

    Determinista: depende solo del texto de entrada.
    """
    freq = Counter(
        w for w in re.findall(r"[A-Za-zÁ-ú]{4,}", texto.lower()) if w not in STOPWORDS
    )
    return [w for w, _ in freq.most_common(n)] or ["concepto"]
