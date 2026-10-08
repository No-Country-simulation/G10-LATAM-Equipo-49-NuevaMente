"""Pantalla 2 — selección de opciones de adaptación."""

import streamlit as st

import api_client


PERFILES = [
    {
        "titulo": "Principiante / Transición de carrera",
        "descripcion": "sin experiencia previa o en proceso de cambio",
        "valor": "Principiante / Transición de Carrera",
    },
    {
        "titulo": "Desarrollador junior / semi senior",
        "descripcion": "con conocimientos básicos o intermedios.",
        "valor": "Desarrollador Junior / Semi Senior",
    },
    {
        "titulo": "Líder técnico / arquitecto",
        "descripcion": "perfil técnico con responsabilidades de diseño y arquitectura.",
        "valor": "Líder Técnico / Arquitecto",
    },
    {
        "titulo": "Gestor / ejecutivo (no técnico)",
        "descripcion": "interesado en la visión general y el impacto del negocio.",
        "valor": "Gestor / Ejecutivo (No Técnico)",
    },
]


FORMATOS = [
    {
        "titulo": "Guía práctica",
        "descripcion": "paso a paso. Tutorial con ejemplos y ejercicios.",
        "valor": "Guía Práctica Paso a Paso (Tutorial)",
    },
    {
        "titulo": "Flashcards",
        "descripcion": "de memorización. Conceptos clave en formato de tarjetas.",
        "valor": "Flashcards de Memorización",
    },
    {
        "titulo": "Quiz interactivo",
        "descripcion": "con justificaciones. Preguntas y respuestas con explicaciones.",
        "valor": "Quiz Interactivo con Justificaciones",
    },
    {
        "titulo": "Resumen ejecutivo (TL;DR)",
        "descripcion": "Visión general y puntos principales.",
        "valor": "Resumen Ejecutivo (TL;DR)",
    },
    {
        "titulo": "Guion de clase / video",
        "descripcion": "Estructura lista para presentación o video.",
        "valor": "Guion de Clase / Video",
    },
]


NICHOS = [
    {
        "titulo": "Fintech",
        "descripcion": "Servicios financieros y tecnología.",
        "valor": "Fintech",
    },
    {
        "titulo": "Salud",
        "descripcion": "Sector salud y ciencias de la vida.",
        "valor": "Salud",
    },
    {
        "titulo": "E-commerce",
        "descripcion": "Comercio electrónico y retail.",
        "valor": "E-commerce",
    },
    {
        "titulo": "General",
        "descripcion": "Aplicable a cualquier industria.",
        "valor": "General",
    },
]


def _selection_styles() -> None:
    """Carga los estilos propios de la pantalla de selección."""

    st.markdown(
        """
<style>

/* =========================================================
   PÁGINA
   ========================================================= */

.nm-selection-title {
    font-size: 30px;
    font-weight: 700;
    line-height: 1.2;
    color: #111111;
    margin: 0 0 5px 0;
}

.nm-selection-subtitle {
    font-size: 24px;
    line-height: 1.4;
    color: #666666;
    margin-bottom: 16px;
}


/* =========================================================
   RESUMEN DEL ARCHIVO
   ========================================================= */

.nm-file-summary {
    background: #F1F1F1;
    border-radius: 15px;
    padding: 12px 18px;
    margin-bottom: 8px;
}

.nm-file-summary-label {
    font-size: 14px;
    line-height: 1.3;
    color: #111111;
    margin-bottom: 3px;
}

.nm-file-summary-name {
    font-size: 14px;
    line-height: 1.35;
    color: #111111;
}


/* =========================================================
   ENCABEZADO DE SECCIÓN
   ========================================================= */

.nm-section-header {
    background: #F1F1F1;
    border-radius: 15px;
    padding: 11px 12px;
    margin-top: 9px;
    margin-bottom: 10px;
}

.nm-section-title {
    font-size: 22px;
    font-weight: 700;
    line-height: 1.3;
    color: #111111;
    margin-bottom: 3px;
}

.nm-section-description {
    font-size: 14px;
    line-height: 1.35;
    color: #666666;
}


/* =========================================================
   TARJETAS
   ========================================================= */

[class*="st-key-perfil_"] button,
[class*="st-key-formato_"] button,
[class*="st-key-nicho_"] button {

    position: relative !important;

    width: 100% !important;

    min-height: 125px !important;
    height: 125px !important;

    padding: 15px 40px 15px 15px !important;

    border-radius: 7px !important;

    text-align: left !important;

    white-space: normal !important;
    word-break: normal !important;

    box-shadow: none !important;

    transition:
        background-color 0.15s ease,
        border-color 0.15s ease;

    overflow: visible !important;
}


/* =========================================================
   TARJETA NO SELECCIONADA
   ========================================================= */

[class*="st-key-perfil_"] button[kind="secondary"],
[class*="st-key-formato_"] button[kind="secondary"],
[class*="st-key-nicho_"] button[kind="secondary"] {

    background: #E5E5E5 !important;

    border: 1px solid #E5E5E5 !important;

    color: #111111 !important;
}

[class*="st-key-perfil_"] button[kind="secondary"]:hover,
[class*="st-key-formato_"] button[kind="secondary"]:hover,
[class*="st-key-nicho_"] button[kind="secondary"]:hover {

    background: #DDDDDD !important;

    border-color: #DDDDDD !important;
}


/* =========================================================
   TARJETA SELECCIONADA
   ========================================================= */

[class*="st-key-perfil_"] button[kind="primary"],
[class*="st-key-formato_"] button[kind="primary"],
[class*="st-key-nicho_"] button[kind="primary"] {

    background: #D7ECFF !important;

    border: 2px solid #0282FB !important;

    color: #111111 !important;
}


/* =========================================================
   TEXTO DE LAS TARJETAS
   ========================================================= */

[class*="st-key-perfil_"] button p,
[class*="st-key-formato_"] button p,
[class*="st-key-nicho_"] button p {

    font-size: 14px !important;

    line-height: 1.45 !important;

    margin: 0 !important;

    overflow: visible !important;

    text-overflow: clip !important;

    white-space: normal !important;

    word-break: normal !important;
}

[class*="st-key-perfil_"] button strong,
[class*="st-key-formato_"] button strong,
[class*="st-key-nicho_"] button strong {

    font-size: 16px !important;

    line-height: 1.35 !important;

    white-space: normal !important;

    word-break: normal !important;
}


/* =========================================================
   CÍRCULO DE SELECCIÓN
   ========================================================= */

[class*="st-key-perfil_"] button[kind="secondary"]::after,
[class*="st-key-formato_"] button[kind="secondary"]::after,
[class*="st-key-nicho_"] button[kind="secondary"]::after {

    content: "";

    position: absolute;

    top: 12px;
    right: 12px;

    width: 14px;
    height: 14px;

    border-radius: 50%;

    background: #FFFFFF;

    border: 1px solid #BDBDBD;
}


[class*="st-key-perfil_"] button[kind="primary"]::after,
[class*="st-key-formato_"] button[kind="primary"]::after,
[class*="st-key-nicho_"] button[kind="primary"]::after {

    content: "";

    position: absolute;

    top: 12px;
    right: 12px;

    width: 14px;
    height: 14px;

    border-radius: 50%;

    background: #0282FB;

    border: 1px solid #0282FB;

    box-shadow:
        inset 0 0 0 3px #D7ECFF;
}


/* =========================================================
   BOTÓN SIGUIENTE
   ========================================================= */

.nm-next-container {
    margin-top: 16px;
}

.nm-next-container + div button {

    min-width: 115px !important;

    height: 37px !important;

    padding: 6px 15px !important;

    border-radius: 7px !important;

    font-size: 12px !important;

    font-weight: 600 !important;
}


/* =========================================================
   TABLET
   ========================================================= */

@media (max-width: 900px) {

    [data-testid="stHorizontalBlock"] {
        gap: 0.75rem !important;
    }
}


/* =========================================================
   MÓVIL
   ========================================================= */

@media (max-width: 600px) {

    /*
     * En celular:
     *
     * Perfil  -> 2 columnas
     * Formato -> 2 columnas
     * Nicho   -> 2 columnas
     */

    [data-testid="stHorizontalBlock"] {

        display: grid !important;

        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;

        gap: 0.7rem !important;

        width: 100% !important;
    }


    /*
     * Cada columna ocupa su celda.
     */

    [data-testid="stHorizontalBlock"] > div {

        width: auto !important;

        min-width: 0 !important;

        max-width: none !important;

        flex: none !important;
    }


    /*
     * La altura se adapta al contenido.
     */

    [class*="st-key-perfil_"] button,
    [class*="st-key-formato_"] button,
    [class*="st-key-nicho_"] button {

        width: 100% !important;

        min-height: 145px !important;

        height: auto !important;

        padding: 18px 42px 18px 18px !important;

        overflow: visible !important;
    }


    /*
     * El texto tampoco tiene límite de altura.
     */

    [class*="st-key-perfil_"] button p,
    [class*="st-key-formato_"] button p,
    [class*="st-key-nicho_"] button p {

        overflow: visible !important;

        text-overflow: clip !important;

        white-space: normal !important;

        word-break: normal !important;
    }


    [class*="st-key-perfil_"] button strong,
    [class*="st-key-formato_"] button strong,
    [class*="st-key-nicho_"] button strong {

        white-space: normal !important;

        word-break: normal !important;
    }
}


/* =========================================================
   TELÉFONO MUY PEQUEÑO
   ========================================================= */

@media (max-width: 420px) {

    [data-testid="stHorizontalBlock"] {

        display: grid !important;

        grid-template-columns:
            repeat(2, minmax(0, 1fr)) !important;

        gap: 0.6rem !important;
    }


    [data-testid="stHorizontalBlock"] > div {

        width: auto !important;

        min-width: 0 !important;

        max-width: none !important;

        flex: none !important;
    }


    [class*="st-key-perfil_"] button,
    [class*="st-key-formato_"] button,
    [class*="st-key-nicho_"] button {

        min-height: 145px !important;

        height: auto !important;

        padding: 18px 40px 18px 16px !important;
    }
}

</style>
        """,
        unsafe_allow_html=True,
    )


def _render_page_header() -> None:
    """Renderiza el encabezado de la página."""

    st.markdown(
        '<div class="nm-selection-title">Seleccionar opciones</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nm-selection-subtitle">'
        "Configura cómo quieres que se procese tu material técnico."
        "</div>",
        unsafe_allow_html=True,
    )


def _render_file_summary(ingest: dict) -> None:
    """Renderiza el resumen del archivo seleccionado."""

    filename = ingest.get(
        "filename",
        "Archivo seleccionado",
    )

    html = (
        '<div class="nm-file-summary">'
        '<div class="nm-file-summary-label">Título del archivo</div>'
        f'<div class="nm-file-summary-name">{filename}</div>'
        "</div>"
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def _render_section_header(
    number: int,
    title: str,
    description: str,
) -> None:
    """Renderiza el encabezado visual de una sección."""

    html = (
        '<div class="nm-section-header">'
        f'<div class="nm-section-title">{number}. {title}</div>'
        f'<div class="nm-section-description">{description}</div>'
        "</div>"
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def _render_option_cards(
    options: list[dict],
    state_key: str,
    key_prefix: str,
    columns: int,
) -> dict:
    """Renderiza las tarjetas seleccionables."""

    if state_key not in st.session_state:
        st.session_state[state_key] = options[0]["titulo"]

    current = st.session_state[state_key]

    cols = st.columns(
        columns,
        gap="small",
    )

    for index, option in enumerate(options):

        with cols[index]:

            selected = current == option["titulo"]

            label = (
                f"**{option['titulo']}**  \n"
                f"{option['descripcion']}"
            )

            if st.button(
                label,
                key=f"{key_prefix}_{index}",
                type="primary" if selected else "secondary",
                width="stretch",
            ):
                st.session_state[state_key] = option["titulo"]
                st.rerun()

    selected_option = next(
        option
        for option in options
        if option["titulo"] == st.session_state[state_key]
    )

    return selected_option


def _render_next_button(
    ingest: dict,
    perfil: dict,
    formato: dict,
    nicho: dict,
) -> None:
    """Renderiza y procesa el botón Siguiente."""

    st.markdown(
        '<div class="nm-next-container"></div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Siguiente →",
        key="selection_next",
        type="primary",
    ):

        try:

            job = api_client.request_adapt(
                ingest["document_id"],
                perfil["valor"],
                formato["valor"],
                nicho["valor"],
            )

        except api_client.ApiError as exc:

            st.session_state["error"] = {
                "code": exc.code,
                "message": exc.message,
            }

            st.session_state["error_back"] = (
                "upload"
                if exc.status_code == 404
                else "selection"
            )

            st.session_state["stage"] = "error"

            st.rerun()

            return

        st.session_state["job_id"] = job["job_id"]

        st.session_state["stage"] = "loading"

        st.rerun()


def render() -> None:
    """Renderiza la pantalla completa de selección."""

    ingest = st.session_state.get("ingest")

    if not ingest:

        st.session_state["stage"] = "upload"

        st.rerun()

        return

    _selection_styles()

    # =============================================================
    # ENCABEZADO
    # =============================================================

    _render_page_header()

    # =============================================================
    # ARCHIVO
    # =============================================================

    _render_file_summary(ingest)

    # =============================================================
    # 1. PERFIL
    # =============================================================

    _render_section_header(
        1,
        "Perfil del destinatario",
        "selecciona el nivel del conocimiento y rol de tu audiencia.",
    )

    perfil = _render_option_cards(
        options=PERFILES,
        state_key="selected_perfil",
        key_prefix="perfil",
        columns=4,
    )

    # =============================================================
    # 2. FORMATO
    # =============================================================

    _render_section_header(
        2,
        "Formato pedagógico de salida",
        "Selecciona el tipo de contenido que deseas generar.",
    )

    formato = _render_option_cards(
        options=FORMATOS,
        state_key="selected_formato",
        key_prefix="formato",
        columns=5,
    )

    # =============================================================
    # 3. NICHO
    # =============================================================

    _render_section_header(
        3,
        "Nicho / contexto de aplicación",
        "Selecciona el área donde se aplicará el contenido.",
    )

    nicho = _render_option_cards(
        options=NICHOS,
        state_key="selected_nicho",
        key_prefix="nicho",
        columns=4,
    )

    # =============================================================
    # SIGUIENTE
    # =============================================================

    _render_next_button(
        ingest=ingest,
        perfil=perfil,
        formato=formato,
        nicho=nicho,
    )
