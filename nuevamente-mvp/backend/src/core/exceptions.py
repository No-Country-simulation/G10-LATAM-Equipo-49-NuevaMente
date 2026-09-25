class NuevaMenteError(Exception):
    """Excepción base del dominio."""


class InvalidFileError(NuevaMenteError):
    code = "INVALID_FILE"


class ScannedPdfError(NuevaMenteError):
    code = "SCANNED_PDF"


class DocumentNotFoundError(NuevaMenteError):
    code = "DOCUMENT_NOT_FOUND"


class NoContextError(NuevaMenteError):
    code = "NO_CONTEXT"


class LLMProviderError(NuevaMenteError):
    code = "LLM_ERROR"


class StorageError(NuevaMenteError):
    code = "STORAGE_ERROR"
