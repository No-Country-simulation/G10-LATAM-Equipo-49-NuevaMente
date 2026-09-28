"""Modelo DocumentChunk (TASK-001, COMP-02).

Fuente literal del Plan Técnico (Fase 9, TASK-001), con un campo agregado
(`page`) — ver nota de diseño abajo. Este archivo SÍ define los campos del
schema (es un contrato de datos), pero los validadores quedan como firma
únicamente: la lógica de validación es implementación futura.
"""
from pydantic import BaseModel, field_validator, model_validator


class DocumentChunk(BaseModel):
    """Fragmento de texto con metadata de posición, usado por todo el
    pipeline (RNF-006 — trazabilidad).

    Campos (TASK-001): id, doc_id, text, position, section, char_start, char_end.

    Nota de diseño (no está en TASK-001 original): se agrega `page:
    int | None` porque el contrato de salida de Fase 6 exige
    `sources: [{chunk_id, page}]`, y no hay otro lugar definido en el Plan
    Técnico donde un chunk conserve su página de origen. Documentado en
    docs/architecture.md.
    """

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
        """Debe rechazar `text` vacío o solo espacios. Implementación futura."""
        ...

    @model_validator(mode="after")
    def validate_positions(self):
        """Debe exigir `char_start < char_end`. Implementación futura."""
        ...
