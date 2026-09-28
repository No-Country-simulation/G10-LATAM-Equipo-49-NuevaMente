"""Modelo DocumentChunk (TASK-001, COMP-02).

Fuente literal del Plan Técnico (Fase 9, TASK-001), con un campo agregado
(`page`). Validadores ejecutables para producir chunks siempre consistentes.
"""
from pydantic import BaseModel, field_validator, model_validator


class DocumentChunk(BaseModel):
    """Fragmento de texto con metadata de posición, usado por todo el
    pipeline (RNF-006 — trazabilidad)."""

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
    def validate_positions(self):
        """Exige `char_start < char_end`."""
        if self.char_start >= self.char_end:
            raise ValueError("char_start debe ser menor a char_end")
        return self