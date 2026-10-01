"""Modelo DocumentChunk (TASK-001, COMP-02).

Fuente: Plan Técnico (Fase 9, TASK-001), con un campo agregado (`page`) para
poder construir `sources: [{chunk_id, page}]` del contrato de salida
(Fase 6, RNF-006). Ver docs/architecture.md, "Decisiones de diseño".
"""
from typing import Self

from pydantic import BaseModel, field_validator, model_validator


class DocumentChunk(BaseModel):
    """Fragmento de texto con metadata de posición, usado por todo el pipeline."""

    id: str
    doc_id: str
    text: str
    position: int
    section: str | None = None
    page: int | None = None
    char_start: int
    char_end: int

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """Rechaza `text` vacío o solo espacios."""
        if not value.strip():
            raise ValueError("text no puede estar vacío")
        return value

    @model_validator(mode="after")
    def validate_positions(self) -> Self:
        """Exige `0 <= char_start < char_end` y `position >= 0`."""
        if self.char_start < 0 or self.position < 0:
            raise ValueError("position y char_start no pueden ser negativos")
        if self.char_start >= self.char_end:
            raise ValueError("char_start debe ser menor que char_end")
        return self
