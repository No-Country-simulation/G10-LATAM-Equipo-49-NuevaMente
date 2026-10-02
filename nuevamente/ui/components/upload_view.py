"""Pantalla 1 — upload_view (UX-001): subir el documento."""
import streamlit as st

import api_client

MAX_MB = 10


def render() -> None:
    st.header("1. Sube tu documento técnico")
    st.write(f"Formatos permitidos: **PDF, Markdown (.md) y texto (.txt)** · máximo {MAX_MB} MB.")

    uploaded = st.file_uploader("Documento", type=["pdf", "md", "markdown", "txt"])

    if st.button("Procesar documento", type="primary", disabled=uploaded is None):
        with st.spinner("Procesando el documento…"):
            try:
                result = api_client.ingest(uploaded.getvalue(), uploaded.name)
            except api_client.ApiError as exc:
                st.session_state["error"] = {"code": exc.code, "message": exc.message}
                st.session_state["error_back"] = "upload"
                st.session_state["stage"] = "error"
                st.rerun()
                return
        st.session_state["ingest"] = result
        st.session_state["stage"] = "selection"
        st.rerun()

