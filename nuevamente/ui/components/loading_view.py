"""Pantalla 3 — loading_view (UX-001): esperar el resultado (polling)."""
import time

import api_client
import streamlit as st

POLL_SECONDS = 1.0
TIMEOUT_SECONDS = 60


def render() -> None:
    job_id = st.session_state.get("job_id")
    if not job_id:
        st.session_state["stage"] = "selection"
        st.rerun()
        return

    st.header("3. Generando contenido…")
    deadline = time.monotonic() + TIMEOUT_SECONDS

    with st.spinner("Esto puede tardar unos segundos."):
        while time.monotonic() < deadline:
            try:
                result = api_client.poll_adapt_result(job_id)
            except api_client.ApiError as exc:
                st.session_state["error"] = {"code": exc.code, "message": exc.message}
                st.session_state["error_back"] = "selection"
                st.session_state["stage"] = "error"
                st.rerun()
                return
            if result.get("status") not in api_client.PENDING_STATUSES:
                st.session_state["result"] = result
                st.session_state["stage"] = "result"
                st.rerun()
                return
            time.sleep(POLL_SECONDS)

    st.session_state["error"] = {
        "code": "API_TIMEOUT",
        "message": f"La generación superó los {TIMEOUT_SECONDS} segundos.",
    }
    st.session_state["error_back"] = "selection"
    st.session_state["stage"] = "error"
    st.rerun()

