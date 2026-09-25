import time
import streamlit as st
from ui.api_client import poll_result


def render_processing():
    st.subheader("Generando contenido...")
    placeholder = st.empty()

    for _ in range(60):
        result = poll_result(st.session_state["job_id"])
        status = result.get("status")

        if status in ("QUEUED", "PROCESSING"):
            placeholder.info("Recuperando información, generando y validando...")
            time.sleep(1)
            continue

        st.session_state["result"] = result
        st.session_state["step"] = "error" if status == "ERROR" else "result"
        st.rerun()

    st.warning("La generación está tardando más de lo esperado. Intenta de nuevo en unos segundos.")
