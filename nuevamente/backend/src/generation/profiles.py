"""Catálogo declarativo de perfiles y formatos pedagógicos del MVP.

Fuente: GEN-001 (4 perfiles), GEN-002 (≥2 formatos MVP), REQ-24. Ampliable
vía GEN-006/GEN-007 sin romper `generation/models.py` (que acepta `str`
libre, no un Enum cerrado).
"""

PERFILES_MVP: list[str] = [
    "principiante",
    "developer",
    "lider_tecnico",
    "ejecutivo",
]

FORMATOS_MVP: list[str] = [
    "tutorial",
    "resumen_ejecutivo",
    # GEN-006: formatos restantes (SHOULD_HAVE) — quiz, flashcards, guion.
]
