"""Configuración/credenciales de OCI (OCI-001).

Fuente: `settings.OCI_CONFIG_FILE`, `settings.OCI_PROFILE` — nunca
credenciales hardcodeadas (RNF-001, SEC-001).
"""


def load_oci_config() -> dict:
    """Carga el perfil de `~/.oci/config` indicado por la configuración.

    Implementación futura — NO debe realizar ninguna llamada real al SDK
    de OCI en esta fase.
    """
    ...
