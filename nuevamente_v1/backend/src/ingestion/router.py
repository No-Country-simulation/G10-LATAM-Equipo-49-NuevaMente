"""Orquestador de ingesta (BE-ING-001, COMP-01).

Responsabilidad (Fase 5): recibir el archivo, detectar su tipo, delegar en
el extractor correspondiente, validar tamaño y devolver un `IngestResult`
con un `document_id` nuevo. NO sube a OCI (eso es `storage/upload.py`,
invocado por `api/orchestrator.py`, no por este módulo — mantener COMP-01
y COMP-09 desacoplados, RNF-005).
"""
from src.ingestion.models import IngestResult


class IngestionRouter:
    """Punto de entrada único de la capa de ingesta."""

    def ingest(self, filename: str, content: bytes) -> IngestResult:
        """Valida, detecta el tipo y extrae el texto de `content`.

        Pasos previstos (implementación futura):
            1. `validators.validate_size(content)`
            2. `validators.detect_type(filename)`
            3. Delegar en el extractor correspondiente
               (`pdf_extractor` | `md_extractor` | `txt_extractor`)
            4. Generar un `document_id` único
            5. Construir y devolver `IngestResult`

        Lanza:
            InvalidFileError, ScannedPdfError — ver cada extractor/validador.

        Implementación futura.
        """
        ...
