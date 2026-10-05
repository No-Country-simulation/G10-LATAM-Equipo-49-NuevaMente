"""Punto de entrada de la interfaz web de NuevaMente.

Ejecutar desde la raíz del proyecto:

    streamlit run ui/app.py
"""

from pathlib import Path

import streamlit as st
from components import (
    error_view,
    loading_view,
    result_view,
    selection_view,
    upload_view,
)
from components.styles import load_styles

# ============================================================
# RUTAS
# ============================================================

UI_DIR = Path(__file__).resolve().parent

LOGO_PATH = UI_DIR / "assets" / "logo.png"


# ============================================================
# PANTALLAS
# ============================================================

SCREENS = {
    "upload": upload_view.render,
    "selection": selection_view.render,
    "loading": loading_view.render,
    "result": result_view.render,
    "error": error_view.render,
}


# ============================================================
# PASOS DEL FLUJO
# ============================================================

STEPS = [
    ("upload", "Cargar archivo"),
    ("selection", "Seleccionar opciones"),
    ("loading", "Procesando"),
    ("result", "Resultados"),
]


# ============================================================
# SIDEBAR
# ============================================================


def render_sidebar() -> None:
    """Renderiza la barra lateral de NuevaMente."""

    current_stage = st.session_state.get(
        "stage",
        "upload",
    )

    # Si estamos en error, mantenemos visualmente
    # el paso donde ocurrió el error.
    if current_stage == "error":
        current_stage = st.session_state.get(
            "error_back",
            "upload",
        )

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        if LOGO_PATH.exists():

            st.image(
                str(LOGO_PATH),
                width=145,
            )

        else:

            st.markdown(
                """
                <div class="fallback-logo">
                    NuevaMente
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------
        # SEPARADOR
        # ----------------------------------------------------

        st.markdown(
            '<div class="sidebar-separator"></div>',
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # CALCULAR PASO ACTUAL
        # ----------------------------------------------------

        current_index = next(
            (
                index
                for index, (stage, _) in enumerate(
                    STEPS,
                    start=1,
                )
                if stage == current_stage
            ),
            1,
        )

        # ----------------------------------------------------
        # STEPPER
        # ----------------------------------------------------

        for index, (stage, label) in enumerate(
            STEPS,
            start=1,
        ):

            # ----------------------------------------------
            # Determinar estado
            # ----------------------------------------------

            if stage == current_stage:

                state = "active"

            elif index < current_index:

                state = "completed"

            else:

                state = "inactive"

            # ----------------------------------------------
            # Número o check
            # ----------------------------------------------

            if state == "completed":

                number = "✓"

            else:

                number = str(index)

            # ----------------------------------------------
            # Render del paso
            # ----------------------------------------------

            step_html = (
                f'<div class="step-item {state}">'
                f'<span class="step-circle">{number}</span>'
                f'<span class="step-label">{label}</span>'
                f"</div>"
            )

            st.markdown(
                step_html,
                unsafe_allow_html=True,
            )


# ============================================================
# APLICACIÓN PRINCIPAL
# ============================================================


def main() -> None:
    """Ejecuta la aplicación NuevaMente."""

    # --------------------------------------------------------
    # CONFIGURACIÓN DE STREAMLIT
    # --------------------------------------------------------

    st.set_page_config(
        page_title="NuevaMente",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --------------------------------------------------------
    # CARGAR ESTILOS
    # --------------------------------------------------------

    load_styles()

    # --------------------------------------------------------
    # ESTADO INICIAL
    # --------------------------------------------------------

    st.session_state.setdefault(
        "stage",
        "upload",
    )

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    render_sidebar()

    # --------------------------------------------------------
    # PANTALLA ACTUAL
    # --------------------------------------------------------

    screen = SCREENS.get(
        st.session_state["stage"],
        upload_view.render,
    )

    screen()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()
