"""Punto de entrada de la interfaz web (COMP-10, FE-UI-005).

Ejecutar desde la raíz del proyecto:  streamlit run ui/app.py

Compone las 5 pantallas de UX-001 (upload → selección → loading → resultado →
error) con una pequeña máquina de estados en `st.session_state["stage"]`.
"""
import streamlit as st

import api_client
from components import error_view, loading_view, result_view, selection_view, upload_view

SCREENS = {
    "upload": upload_view.render,
    "selection": selection_view.render,
    "loading": loading_view.render,
    "result": result_view.render,
    "error": error_view.render,
}


def main() -> None:
    """Renderiza la pantalla correspondiente al estado actual del flujo."""
    st.set_page_config(page_title="NuevaMente", page_icon="🧠", layout="centered")
    st.title("🧠 NuevaMente")
    st.caption("Adaptación de documentación técnica a contenido educativo")

    st.session_state.setdefault("stage", "upload")

    with st.sidebar:
        st.subheader("Estado")
        if api_client.health():
            st.success("API conectada")
        else:
            st.error("API no disponible")
        st.caption(f"URL: {api_client.API_URL}")
        st.caption("Modo mock: sin RAG ni LLM (Semana 2).")

    SCREENS.get(st.session_state["stage"], upload_view.render)()


if __name__ == "__main__":
    main()
