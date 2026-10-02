"""Pantalla 5 — error_view (UX-001): mostrar el error y cómo continuar."""
import streamlit as st

_HINTS = {
    "INVALID_FILE": "Revisa que el archivo sea PDF, MD o TXT, no esté vacío y pese menos de 10 MB.",
    "SCANNED_PDF": "El PDF parece una imagen escaneada. Sube una versión con texto seleccionable.",
    "DOCUMENT_TOO_LARGE": "Divide el documento en partes más pequeñas.",
    "DOCUMENT_NOT_FOUND": "La API ya no recuerda el documento. Vuelve a subirlo.",
    "API_UNREACHABLE": "Enciende la API (`run_api`) y vuelve a intentarlo.",
    "STORAGE_ERROR": "El almacenamiento no está disponible. Revisa la configuración.",
}


def render() -> None:
    error = st.session_state.get("error") or {"code": "INTERNAL_ERROR", "message": "Error."}

    st.header("Algo salió mal")
    st.error(f"**{error['code']}** — {error['message']}")
    hint = _HINTS.get(error["code"])
    if hint:
        st.caption(hint)

    back = st.session_state.get("error_back", "upload")
    if st.button("Volver a intentar", type="primary"):
        st.session_state.pop("error", None)
        if back == "selection" and not st.session_state.get("ingest"):
            back = "upload"
        st.session_state["stage"] = back
        st.rerun()