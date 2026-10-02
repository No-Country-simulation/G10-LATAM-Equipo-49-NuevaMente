"""Pantalla 2 — selection_view (UX-001): elegir perfil, formato, nicho y detalle."""
import streamlit as st

import api_client

PERFILES = ["principiante", "developer", "lider_tecnico", "ejecutivo"]
FORMATOS = ["tutorial", "resumen_ejecutivo"]
NIVELES = ["breve", "estandar", "profundo"]


def _summary(ingest: dict) -> None:
    st.success(f"Documento procesado: **{ingest.get('filename', '')}**")
    cols = st.columns(3)
    cols[0].metric("Fragmentos", ingest.get("chunk_count", "—"))
    cols[1].metric("Páginas", ingest.get("page_count") or "—")
    cols[2].metric("Caracteres", f"{ingest.get('char_count', 0):,}")
    st.caption(f"document_id: `{ingest['document_id']}`")
    for warning in ingest.get("warnings", []):
        st.warning(warning)


def render() -> None:
    ingest = st.session_state.get("ingest")
    if not ingest:
        st.session_state["stage"] = "upload"
        st.rerun()
        return

    _summary(ingest)
    st.header("2. Elige cómo adaptar el contenido")

    perfil = st.selectbox("Perfil de la audiencia", PERFILES)
    formato = st.selectbox("Formato pedagógico", FORMATOS)
    nicho = st.text_input("Nicho / contexto (opcional)", placeholder="p. ej. cloud computing")
    nivel = st.select_slider("Nivel de detalle", options=NIVELES, value="estandar")

    col_generate, col_new = st.columns(2)
    if col_generate.button("Generar contenido adaptado", type="primary"):
        try:
            job = api_client.request_adapt(ingest["document_id"], perfil, formato, nicho, nivel)
        except api_client.ApiError as exc:
            st.session_state["error"] = {"code": exc.code, "message": exc.message}
            st.session_state["error_back"] = "upload" if exc.status_code == 404 else "selection"
            st.session_state["stage"] = "error"
            st.rerun()
            return
        st.session_state["job_id"] = job["job_id"]
        st.session_state["stage"] = "loading"
        st.rerun()

    if col_new.button("Subir otro documento"):
        for key in ("ingest", "job_id", "result"):
            st.session_state.pop(key, None)
        st.session_state["stage"] = "upload"
        st.rerun()
