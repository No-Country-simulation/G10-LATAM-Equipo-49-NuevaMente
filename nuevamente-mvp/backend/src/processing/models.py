from pydantic import BaseModel, field_validator, model_validator


class DocumentChunk(BaseModel):
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
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text no puede estar vacío")
        return value

    @model_validator(mode="after")
    def validate_positions(self):
        if self.char_start >= self.char_end:
            raise ValueError("char_start debe ser menor que char_end")
        return self
