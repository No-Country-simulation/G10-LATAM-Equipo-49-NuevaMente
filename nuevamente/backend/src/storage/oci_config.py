"""Configuración/credenciales de OCI (OCI-001).

Fuente: `settings.OCI_CONFIG_FILE`, `settings.OCI_PROFILE` — nunca
credenciales hardcodeadas (RNF-001, SEC-001).
"""
from src.core.config import get_settings
from src.core.exceptions import StorageError


def load_oci_config() -> dict:
    """Carga y valida el perfil de `~/.oci/config` indicado por la configuración.

    Lanza:
        StorageError: si el SDK no está instalado o la configuración es inválida.
    """
    settings = get_settings()
    try:
        import oci
    except ImportError as exc:
        raise StorageError(
            "El SDK de OCI no está instalado. Ejecute: pip install -r requirements-oci.txt"
        ) from exc

    try:
        config = oci.config.from_file(
            file_location=str(settings.resolve_path(settings.OCI_CONFIG_FILE)),
            profile_name=settings.OCI_PROFILE,
        )
        oci.config.validate_config(config)
    except Exception as exc:
        raise StorageError(f"Configuración de OCI inválida: {exc}") from exc
    return config