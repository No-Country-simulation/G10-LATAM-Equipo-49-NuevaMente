import streamlit as st


def render_error():
    st.error("Ocurrió un problema al generar el contenido. Intenta nuevamente.")
    if st.button("Volver a intentar"):
        st.session_state["step"] = "configuration"
        st.rerun()
