import streamlit as st

from ui.components.upload_view import render_upload
from ui.components.selection_view import render_selection
from ui.components.loading_view import render_processing
from ui.components.result_view import render_result
from ui.components.error_view import render_error

st.set_page_config(page_title="NuevaMente", layout="centered")

if "step" not in st.session_state:
    st.session_state["step"] = "upload"

STEP_RENDERERS = {
    "upload": render_upload,
    "configuration": render_selection,
    "processing": render_processing,
    "result": render_result,
    "error": render_error,
}

STEP_RENDERERS[st.session_state["step"]]()
