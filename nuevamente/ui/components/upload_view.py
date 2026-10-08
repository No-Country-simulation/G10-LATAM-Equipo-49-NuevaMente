"""Pantalla 1 — Cargar archivo de NuevaMente."""

import html

import streamlit as st

import api_client

MAX_MB = 10


def render() -> None:
    """Renderiza la pantalla de carga."""

    st.markdown(
        """
        <style>
        /* Ocultar únicamente la ficha nativa del archivo de Streamlit */
        [data-testid="stFileChip"] {
            display: none !important;
        }

        /* Ocultar el contenedor de la ficha si queda vacío */
        [data-testid="stFileUploader"] [data-testid="stFileChip"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nm-page-title">Cargar archivo</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nm-page-description">'
        "Sube el documento que deseas procesar. "
        "Aceptamos archivos PDF, DOCX, TXT o imágenes."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        # Los placeholders se crean primero para que el contenido
        # visual aparezca antes del uploader real de Streamlit.
        icon_slot = st.empty()
        title_slot = st.empty()
        subtitle_slot = st.empty()

        uploaded = st.file_uploader(
            "Documento",
            type=["pdf", "docx", "md", "markdown", "txt"],
            label_visibility="collapsed",
        )

        if uploaded is None:
            icon_slot.markdown(
                '<div class="nm-upload-icon">↑</div>',
                unsafe_allow_html=True,
            )
            title_slot.markdown(
                '<div class="nm-upload-title">'
                "Arrastra y suelta tu archivo aquí"
                "</div>",
                unsafe_allow_html=True,
            )
            subtitle_slot.markdown(
                '<div class="nm-upload-subtitle">'
                "o haz clic para seleccionar"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            filename = html.escape(uploaded.name)

            icon_slot.markdown(
                '<div class="nm-success-icon">✓</div>',
                unsafe_allow_html=True,
            )

            title_slot.markdown(
                '<div class="nm-success-title">'
                "Archivo subido correctamente"
                "</div>",
                unsafe_allow_html=True,
            )

            subtitle_slot.markdown(
                f'<div class="nm-file-name">{filename}</div>',
                unsafe_allow_html=True,
            )

    recommendations_html = """
<div class="nm-recommendations">
    <div class="nm-recommendations-icon">💡</div>
    <div class="nm-recommendations-content">
        <div class="nm-recommendations-title">
            Recomendaciones
        </div>
        <div class="nm-recommendations-text">
            • Asegúrate de que el documento no sea ilegible.<br>
            • El archivo no debe superar los 10 MB.<br>
            • Para mejores resultados, utiliza documentos con texto claro y bien estructurado.
        </div>
    </div>
</div>
"""

    st.markdown(
        recommendations_html,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nm-next-row">',
        unsafe_allow_html=True,
    )

    if st.button(
        "Siguiente →",
        key="next_upload",
        use_container_width=True,
        disabled=uploaded is None,
    ):
        try:
            result = api_client.ingest(
                uploaded.getvalue(),
                uploaded.name,
            )
            st.session_state["ingest"] = result
            st.session_state["stage"] = "selection"
            st.rerun()
        except api_client.ApiError as exc:
            st.session_state["error"] = {
                "code": exc.code,
                "message": exc.message,
            }
            st.session_state["error_back"] = "upload"
            st.session_state["stage"] = "error"
            st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )
