"""Pantalla 3 — Procesando documento."""

import time

import api_client
import streamlit as st


POLL_SECONDS = 1.0
MIN_PROCESSING_SECONDS = 6.0


def _render_styles() -> None:
    """Estilos propios de la pantalla de procesamiento."""
    st.html(
        """
        <style>
            .nm-loading-page {
                width: 100%;
            }

            .nm-loading-title {
                font-size: 30px;
                font-weight: 600;
                line-height: 1.2;
                color: #111111;
                margin-bottom: 8px;
            }

            .nm-loading-description {
                font-size: 22px;
                line-height: 1.4;
                color: #666666;
                margin-bottom: 28px;
            }

            .nm-loading-card {
                width: 100%;
                max-width: 760px;
                margin: 0 auto;
                background: #ffffff;
                border: 1px solid #e4e4e4;
                border-radius: 12px;
                padding: 34px 42px 36px;
                box-sizing: border-box;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            }

            .nm-loading-document-icon {
                width: 58px;
                height: 58px;
                margin: 0 auto 18px;
                border-radius: 50%;
                background: #eaf5ff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 27px;
            }

            .nm-loading-card-title {
                font-size: 18px;
                font-weight: 600;
                line-height: 1.3;
                color: #111111;
                margin-bottom: 7px;
            }

            .nm-loading-card-subtitle {
                font-size: 16px;
                line-height: 1.4;
                color: #777777;
                margin-bottom: 25px;
            }

            .nm-progress-wrapper {
                width: 100%;
                margin-bottom: 28px;
            }

            .nm-progress-track {
                width: 100%;
                height: 9px;
                background: #e7e7e7;
                border-radius: 999px;
                overflow: hidden;
            }

            .nm-progress-bar {
                height: 100%;
                background: #0282fb;
                border-radius: 999px;
                transition: width 0.4s ease;
            }

            .nm-loading-steps {
                width: 100%;
                text-align: left;
            }

            .nm-loading-step {
                display: flex;
                align-items: center;
                gap: 12px;
                min-height: 34px;
                font-size: 16px;
                color: #999999;
            }

            .nm-loading-step-dot {
                width: 10px;
                height: 10px;
                flex: 0 0 10px;
                border-radius: 50%;
                background: #d9d9d9;
                box-sizing: border-box;
            }

            .nm-loading-step-dot.active {
                background: #0282fb;
                box-shadow: 0 0 0 4px #eaf5ff;
            }

            .nm-loading-step-dot.done {
                background: #28a745;
                position: relative;
            }

            .nm-loading-step-dot.done::after {
                content: "✓";
                position: absolute;
                color: white;
                font-size: 7px;
                font-weight: 700;
                left: 2px;
                top: 0px;
            }

            .nm-loading-tip {
                width: 100%;
                max-width: 760px;
                margin: 20px auto 0;
                padding: 18px 22px;
                box-sizing: border-box;
                background: #f4f9fd;
                border: 1px solid #dceefb;
                border-radius: 10px;
                display: flex;
                align-items: flex-start;
                gap: 14px;
                text-align: left;
            }

            .nm-loading-tip-icon {
                width: 30px;
                height: 30px;
                flex: 0 0 30px;
                border-radius: 50%;
                background: #e5f3ff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 15px;
            }

            .nm-loading-tip-title {
                font-size: 16px;
                font-weight: 600;
                color: #111111;
                margin-bottom: 4px;
            }

            .nm-loading-tip-text {
                font-size: 16px;
                line-height: 1.5;
                color: #666666;
            }

            @media (max-width: 768px) {
                .nm-loading-card {
                    padding: 28px 22px 30px;
                }

                .nm-loading-title {
                    font-size: 30px;
                }

                .nm-loading-card-title {
                    font-size: 18px;
                }

                .nm-loading-tip {
                    padding: 16px;
                }
            }

            @media (max-width: 480px) {
                .nm-loading-card {
                    padding: 24px 16px 26px;
                }

                .nm-loading-tip {
                    padding: 14px;
                }

                .nm-loading-step {
                    gap: 10px;
                }
            }
        </style>
        """
    )


def _render_step(text: str, status: str) -> str:
    """Construye visualmente un paso del procesamiento."""
    dot_class = "nm-loading-step-dot"

    if status == "active":
        dot_class += " active"
    elif status == "done":
        dot_class += " done"

    return (
        '<div class="nm-loading-step">'
        f'<div class="{dot_class}"></div>'
        f"<div>{text}</div>"
        "</div>"
    )


def _get_step_statuses(progress: int) -> list[str]:
    """Determina qué pasos aparecen pendientes, activos o terminados."""
    if progress <= 20:
        return ["active", "pending", "pending", "pending", "pending"]

    if progress <= 40:
        return ["done", "active", "pending", "pending", "pending"]

    if progress <= 60:
        return ["done", "done", "active", "pending", "pending"]

    if progress <= 80:
        return ["done", "done", "done", "active", "pending"]

    return ["done", "done", "done", "done", "active"]


def _render_loading_card(progress: int) -> None:
    """Renderiza la tarjeta principal de procesamiento."""
    statuses = _get_step_statuses(progress)

    step_texts = [
        "Leyendo y analizando el contenido",
        "Aplicando configuraciones seleccionadas",
        "Generando contenido adaptado",
        "Organizando resultados",
        "Casi listo...",
    ]

    steps = "".join(
        _render_step(text, status)
        for text, status in zip(step_texts, statuses)
    )

    html = f"""
        <div class="nm-loading-card">
            <div class="nm-loading-document-icon">📄</div>

            <div class="nm-loading-card-title">
                Analizando y generando contenido...
            </div>

            <div class="nm-loading-card-subtitle">
                Esto puede tardar un poco, por favor espera.
            </div>

            <div class="nm-progress-wrapper">
                <div class="nm-progress-track">
                    <div
                        class="nm-progress-bar"
                        style="width: {progress}%"
                    ></div>
                </div>
            </div>

            <div class="nm-loading-steps">
                {steps}
            </div>
        </div>
    """

    st.html(html)


def _render_tip() -> None:
    """Renderiza el consejo inferior."""
    st.html(
        """
        <div class="nm-loading-tip">
            <div class="nm-loading-tip-icon">⚙️</div>

            <div>
                <div class="nm-loading-tip-title">
                    ¿Sabías que?
                </div>

                <div class="nm-loading-tip-text">
                    El contenido se adapta al perfil del destinatario,
                    formato pedagógico y contexto que seleccionaste para
                    que sea más relevante y útil.
                </div>
            </div>
        </div>
        """
    )


def _render_page(progress: int) -> None:
    """Renderiza toda la pantalla de procesamiento."""
    st.html(
        """
        <div class="nm-loading-page">
            <div class="nm-loading-title">
                Procesando tu documento
            </div>

            <div class="nm-loading-description">
                Estamos analizando tu material técnico y generando el
                contenido personalizado.
            </div>
        </div>
        """
    )

    _render_loading_card(progress)
    _render_tip()


@st.fragment(run_every=POLL_SECONDS)
def _loading_fragment() -> None:
    """Actualiza periódicamente la pantalla sin rerun de toda la app."""
    job_id = st.session_state.get("job_id")

    if not job_id:
        st.session_state["stage"] = "selection"
        st.rerun()
        return

    progress = st.session_state.get("loading_progress", 8)
    started_at = st.session_state.get("loading_started_at")

    if started_at is None:
        started_at = time.monotonic()
        st.session_state["loading_started_at"] = started_at

    # Renderizamos primero el estado actual.
    _render_page(progress)

    try:
        result = api_client.poll_adapt_result(job_id)

    except api_client.ApiError as exc:
        st.session_state["error"] = {
            "code": exc.code,
            "message": exc.message,
        }

        st.session_state["error_back"] = "selection"
        st.session_state["stage"] = "error"

        st.rerun()
        return

    status = result.get("status")
    elapsed = time.monotonic() - started_at

    # API todavía está procesando.
    if status in api_client.PENDING_STATUSES:
        st.session_state["loading_progress"] = min(
            progress + 12,
            92,
        )
        return

    # La API terminó, pero mantenemos la pantalla unos segundos
    # para que el usuario pueda ver el proceso.
    if elapsed < MIN_PROCESSING_SECONDS:
        st.session_state["loading_progress"] = min(
            progress + 12,
            92,
        )
        return

    # Procesamiento terminado.
    st.session_state["result"] = result
    st.session_state["loading_progress"] = 100

    st.session_state.pop(
        "loading_started_at",
        None,
    )

    st.session_state.pop(
        "loading_job_id",
        None,
    )

    st.session_state["stage"] = "result"

    # Volvemos a ejecutar toda la aplicación solamente una vez,
    # cuando ya terminó el procesamiento.
    st.rerun()


def render() -> None:
    """Punto de entrada de la pantalla de procesamiento."""
    job_id = st.session_state.get("job_id")

    if not job_id:
        st.session_state["stage"] = "selection"
        st.rerun()
        return

    # Inicializamos el estado una sola vez para cada job.
    if st.session_state.get("loading_job_id") != job_id:
        st.session_state["loading_job_id"] = job_id
        st.session_state["loading_started_at"] = time.monotonic()
        st.session_state["loading_progress"] = 8

    # Los estilos se renderizan una sola vez fuera del fragment.
    _render_styles()

    # El fragment se actualiza cada segundo sin volver a ejecutar
    # las demás pantallas de la aplicación.
    _loading_fragment()
