import streamlit as st
from ui.api_client import ingest_file


def render_upload():
    st.title("NuevaMente")
    st.caption("Transforma documentación técnica en contenido educativo.")

    uploaded = st.file_uploader("Selecciona un archivo (PDF, Markdown o TXT, máx. 10 MB)",
                                 type=["pdf", "md", "txt"])

    if uploaded and st.button("Procesar documento"):
        with st.spinner("Ingiriendo e indexando el documento..."):
            try:
                result = ingest_file(uploaded.name, uploaded.getvalue())
                st.session_state["document_id"] = result["document_id"]
                st.session_state["step"] = "configuration"
                st.success(f"Documento cargado correctamente — document_id: {result['document_id']}")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo procesar el documento: {exc}")
