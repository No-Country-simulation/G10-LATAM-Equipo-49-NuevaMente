import streamlit as st
from ui.api_client import request_adaptation


def render_selection():
    st.subheader("Configura la generación")

    perfil = st.radio("Perfil", ["principiante", "developer", "lider_tecnico"])
    formato = st.radio("Formato", ["tutorial", "resumen"])
    nicho = st.text_input("Nicho (opcional)", placeholder="fintech")
    nivel = st.radio("Nivel de detalle", ["breve", "estandar", "profundo"], index=1)

    if st.button("Generar contenido"):
        payload = {
            "document_id": st.session_state["document_id"],
            "perfil": perfil, "formato": formato,
            "nicho": nicho or None, "nivel_detalle": nivel,
        }
        result = request_adaptation(payload)
        st.session_state["job_id"] = result["job_id"]
        st.session_state["step"] = "processing"
        st.rerun()
