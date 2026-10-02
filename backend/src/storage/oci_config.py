"""Configuración/credenciales de OCI (OCI-001).

Fuente: `settings.OCI_CONFIG_FILE`, `settings.OCI_PROFILE` — nunca
credenciales hardcodeadas (RNF-001, SEC-001).
"""
import oci

from src.core.config import get_settings


def load_oci_config() -> dict:
    """Carga el perfil de `~/.oci/config` indicado por la configuración.

    Lee las rutas y nombres de perfil desde `settings` (poblablas vía
    `.env`, nunca hardcodeadas). No expone secretos: el objeto `dict`
    resultante solo vive en el proceso.
    """
    settings = get_settings()
    return oci.config.from_file(
        file_location=settings.OCI_CONFIG_FILE or "~/.oci/config",
        profile_name=settings.OCI_PROFILE or "DEFAULT",
    )