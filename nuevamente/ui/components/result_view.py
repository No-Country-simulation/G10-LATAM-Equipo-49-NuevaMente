"""Pantalla 4 — Resultados."""

import html
import io
import json

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _render_styles() -> None:
    """Estilos propios de la pantalla de resultados."""
    st.html(
        """
        <style>
            .nm-results-page {
                width: 100%;
            }

            .nm-results-header {
                margin-bottom: 18px;
            }

            .nm-results-title {
                font-size: 30px;
                font-weight: 600;
                line-height: 1.2;
                color: #111111;
                margin-bottom: 5px;
            }

            .nm-results-description {
                font-size: 16px;
                line-height: 1.4;
                color: #666666;
            }

            .nm-results-layout {
                display: grid;
                grid-template-columns: minmax(0, 1fr) 265px;
                gap: 14px;
                align-items: start;
            }

            .nm-results-main {
                min-width: 0;
            }

            .nm-results-toolbar {
                display: flex;
                align-items: center;
                gap: 4px;
                width: 100%;
                height: 43px;
                background: #eeeeee;
                border-radius: 7px;
                padding: 4px;
                box-sizing: border-box;
                margin-bottom: 4px;
            }

            .nm-results-toolbar-item {
                height: 35px;
                padding: 0 17px;
                border-radius: 6px;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 16px;
                color: #333333;
                box-sizing: border-box;
            }

            .nm-results-toolbar-item.active {
                background: #0282fb;
                color: #ffffff;
            }

            .nm-results-toolbar-item.download {
                margin-left: auto;
            }

            .nm-results-preview {
                width: 100%;
                min-height: 430px;
                max-height: 600px;
                overflow-y: auto;
                background: #f5f5f5;
                border-radius: 0 0 7px 7px;
                padding: 24px 28px;
                box-sizing: border-box;
                color: #222222;
                font-size: 16px;
                line-height: 1.6;
            }

            .nm-results-preview-content {
                max-width: 720px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 5px;
                padding: 28px 32px;
                box-sizing: border-box;
            }

            .nm-results-preview-content h1 {
                font-size: 22px;
                line-height: 1.3;
                margin-top: 0;
                margin-bottom: 15px;
                color: #111111;
            }

            .nm-results-preview-content h2 {
                font-size: 17px;
                line-height: 1.35;
                margin-top: 22px;
                margin-bottom: 9px;
                color: #111111;
            }

            .nm-results-preview-content h3 {
                font-size: 14px;
                line-height: 1.35;
                margin-top: 18px;
                margin-bottom: 7px;
                color: #111111;
            }

            .nm-results-preview-content p {
                margin-top: 0;
                margin-bottom: 10px;
            }

            .nm-results-preview-content ul,
            .nm-results-preview-content ol {
                padding-left: 22px;
                margin-top: 5px;
                margin-bottom: 12px;
            }

            .nm-results-preview-content code {
                background: #f0f0f0;
                padding: 2px 4px;
                border-radius: 3px;
                font-size: 10px;
            }

            .nm-results-preview-content blockquote {
                border-left: 3px solid #0282fb;
                margin-left: 0;
                padding-left: 12px;
                color: #666666;
            }

            .nm-results-empty {
                min-height: 360px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #888888;
                text-align: center;
            }

            .nm-results-sidebar {
                min-width: 0;
            }

            .nm-results-panel {
                background: #f5f5f5;
                border-radius: 9px;
                padding: 13px 10px;
                box-sizing: border-box;
                margin-bottom: 12px;
            }

            .nm-results-panel-title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 16px;
                color: #666666;
                margin-bottom: 12px;
            }

            .nm-results-panel-title-icon {
                font-size: 18px;
                color: #222222;
            }

            .nm-config-item {
                display: flex;
                align-items: center;
                gap: 10px;
                min-height: 45px;
            }

            .nm-config-icon {
                width: 29px;
                height: 29px;
                flex: 0 0 29px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #ffffff;
                border-radius: 5px;
                font-size: 15px;
            }

            .nm-config-content {
                min-width: 0;
            }

            .nm-config-label {
                font-size: 16px;
                color: #888888;
                margin-bottom: 2px;
            }

            .nm-config-value {
                font-size: 16px;
                line-height: 1.3;
                color: #222222;
                word-break: break-word;
            }

            .nm-actions-panel {
                padding-bottom: 12px;
            }

            .nm-action-title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 16px;
                color: #666666;
                margin-bottom: 9px;
            }

            .nm-action-icon {
                font-size: 18px;
                color: #111111;
            }

            .nm-action-button {
                width: 100%;
                min-height: 28px;
                border: 0;
                border-radius: 6px;
                margin-bottom: 5px;
                padding: 6px 8px;
                background: #e9e9e9;
                color: #222222;
                font-size: 16px;
                cursor: pointer;
                text-align: center;
                box-sizing: border-box;
            }

            .nm-action-button.primary {
                background: #0282fb;
                color: #ffffff;
            }

            .nm-result-info {
                margin-top: 10px;
                padding: 10px 12px;
                border-radius: 7px;
                background: #f5f5f5;
                color: #666666;
                font-size: 16px;
                line-height: 1.4;
            }

            .nm-markdown-container {
                background: #f5f5f5;
                border-radius: 0 0 7px 7px;
                min-height: 430px;
                max-height: 600px;
                overflow-y: auto;
                padding: 18px;
                box-sizing: border-box;
            }

            .nm-markdown-code {
                white-space: pre-wrap;
                word-break: break-word;
                background: #ffffff;
                border-radius: 6px;
                padding: 20px;
                font-family: Consolas, Monaco, monospace;
                font-size: 16px;
                line-height: 1.55;
                color: #222222;
            }

            @media (max-width: 900px) {
                .nm-results-layout {
                    grid-template-columns: 1fr;
                }

                .nm-results-sidebar {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                }

                .nm-results-panel {
                    margin-bottom: 0;
                }
            }

            @media (max-width: 600px) {
                .nm-results-sidebar {
                    grid-template-columns: 1fr;
                }

                .nm-results-toolbar {
                    height: auto;
                    flex-wrap: wrap;
                    padding: 5px;
                }

                .nm-results-toolbar-item {
                    flex: 1 1 auto;
                    justify-content: center;
                }

                .nm-results-toolbar-item.download {
                    margin-left: 0;
                }

                .nm-results-preview {
                    padding: 12px;
                }

                .nm-results-preview-content {
                    padding: 20px 16px;
                }
            }
        </style>
        """
    )


def _get_content(result: dict) -> dict:
    """Obtiene el contenido adaptado de forma segura."""
    return result.get("contenido_adaptado") or {}


def _get_markdown(result: dict) -> str:
    """Construye el Markdown completo del resultado."""
    content = _get_content(result)

    body = content.get("cuerpo", "") or ""
    conceptos = content.get("conceptos_clave", []) or []
    tiempo = content.get("tiempo_estimado_min")

    markdown = body.strip()

    if conceptos:
        markdown += "\n\n## Conceptos clave\n\n"
        markdown += "\n".join(f"- {concepto}" for concepto in conceptos)

    if tiempo:
        markdown += f"\n\n**Tiempo estimado de lectura:** {tiempo} min"

    return markdown.strip()


def _get_filename(result: dict) -> str:
    """Obtiene el nombre del documento procesado."""
    ingest = st.session_state.get("ingest") or {}
    filename = ingest.get("filename")

    if filename:
        return filename

    meta = result.get("metadatos") or {}
    return meta.get("filename", "Documento técnico")


def _generate_pdf(markdown: str, title: str) -> bytes:
    """Genera un PDF sencillo a partir del contenido adaptado."""
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
        title="Resultado NuevaMente",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "NMTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        spaceAfter=14,
    )

    heading_style = ParagraphStyle(
        "NMHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=7,
    )

    body_style = ParagraphStyle(
        "NMBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7,
    )

    story = [
        Paragraph("NuevaMente", title_style),
        Paragraph(html.escape(title), body_style),
        Spacer(1, 10),
    ]

    lines = markdown.splitlines()

    for line in lines:
        stripped = line.strip()

        if not stripped:
            story.append(Spacer(1, 5))
            continue

        if stripped.startswith("### "):
            text = html.escape(stripped[4:])
            story.append(Paragraph(text, heading_style))
            continue

        if stripped.startswith("## "):
            text = html.escape(stripped[3:])
            story.append(Paragraph(text, heading_style))
            continue

        if stripped.startswith("# "):
            text = html.escape(stripped[2:])
            story.append(Paragraph(text, title_style))
            continue

        if stripped.startswith("- "):
            text = html.escape(stripped[2:])
            story.append(Paragraph(f"• {text}", body_style))
            continue

        escaped = html.escape(stripped)

        escaped = escaped.replace("**", "")

        story.append(Paragraph(escaped, body_style))

    document.build(story)

    buffer.seek(0)
    return buffer.getvalue()


def _render_header() -> None:
    """Renderiza el encabezado."""
    st.html(
        """
        <div class="nm-results-header">
            <div class="nm-results-title">
                Resultado generado
            </div>

            <div class="nm-results-description">
                El material técnico ha sido adaptado correctamente.
            </div>
        </div>
        """
    )


def _render_toolbar() -> None:
    """Renderiza la barra superior de la vista previa."""
    st.html(
        """
        <div class="nm-results-toolbar">
            <div class="nm-results-toolbar-item active">
                📄&nbsp;&nbsp; Vista previa
            </div>

            <div class="nm-results-toolbar-item">
                &lt;/&gt;&nbsp;&nbsp; Markdown
            </div>

            <div class="nm-results-toolbar-item download">
                ⬇&nbsp;&nbsp; Descargar
            </div>
        </div>
        """
    )


def _render_preview(markdown: str) -> None:
    """Renderiza el contenido adaptado."""
    if not markdown:
        st.html(
            """
            <div class="nm-results-preview">
                <div class="nm-results-empty">
                    No hay contenido adaptado para mostrar.
                </div>
            </div>
            """
        )
        return

    st.markdown(
        f"""
        <div class="nm-results-preview">
            <div class="nm-results-preview-content">
                {markdown}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_markdown_view(markdown: str) -> None:
    """Renderiza el Markdown como texto."""
    safe_markdown = html.escape(markdown)

    st.html(
        f"""
        <div class="nm-markdown-container">
            <div class="nm-markdown-code">{safe_markdown}</div>
        </div>
        """
    )


def _render_config_panel(result: dict) -> None:
    """Renderiza el resumen de configuración."""
    meta = result.get("metadatos") or {}
    ingest = st.session_state.get("ingest") or {}

    filename = _get_filename(result)
    perfil = meta.get("perfil", "—")
    formato = meta.get("formato", "—")
    nicho = meta.get("nicho", "—")

    if nicho == "—":
        nicho = meta.get("contexto", "—")

    st.html(
        f"""
        <div class="nm-results-panel">
            <div class="nm-results-panel-title">
                <span class="nm-results-panel-title-icon">⚙</span>
                <span>Resumen de tu configuración</span>
            </div>

            <div class="nm-config-item">
                <div class="nm-config-icon">📄</div>
                <div class="nm-config-content">
                    <div class="nm-config-label">
                        Archivo procesado
                    </div>
                    <div class="nm-config-value">
                        {html.escape(filename)}
                    </div>
                </div>
            </div>

            <div class="nm-config-item">
                <div class="nm-config-icon">&lt;/&gt;</div>
                <div class="nm-config-content">
                    <div class="nm-config-label">
                        Perfil del destinatario
                    </div>
                    <div class="nm-config-value">
                        {html.escape(str(perfil))}
                    </div>
                </div>
            </div>

            <div class="nm-config-item">
                <div class="nm-config-icon">📑</div>
                <div class="nm-config-content">
                    <div class="nm-config-label">
                        Formato de salida
                    </div>
                    <div class="nm-config-value">
                        {html.escape(str(formato))}
                    </div>
                </div>
            </div>

            <div class="nm-config-item">
                <div class="nm-config-icon">🏢</div>
                <div class="nm-config-content">
                    <div class="nm-config-label">
                        Nicho/contexto
                    </div>
                    <div class="nm-config-value">
                        {html.escape(str(nicho))}
                    </div>
                </div>
            </div>
        </div>
        """
    )


def _render_actions(result: dict, markdown: str) -> None:
    """Renderiza las acciones del resultado."""
    pdf_data = _generate_pdf(markdown, _get_filename(result))

    st.html(
        """
        <div class="nm-results-panel nm-actions-panel">
            <div class="nm-action-title">
                <span class="nm-action-icon">⬇</span>
                <span>Acciones</span>
            </div>
        </div>
        """
    )

    st.download_button(
        "Descargar resultado (PDF)",
        data=pdf_data,
        file_name="resultado_nuevamente.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
        key="download_pdf",
    )

    st.download_button(
        "Descargar en Markdown",
        data=markdown,
        file_name="resultado_nuevamente.md",
        mime="text/markdown",
        use_container_width=True,
        key="download_markdown",
    )

    copy_html = html.escape(markdown)

    st.html(
        f"""
        <button
            class="nm-action-button"
            onclick="
                navigator.clipboard.writeText(
                    `{copy_html.replace("`", "\\`")}`
                ).then(() => {{
                    this.innerText = '✓ Copiado al portapapeles';
                    setTimeout(() => {{
                        this.innerText = 'Copiar al portapapeles';
                    }}, 1800);
                }});
            "
        >
            Copiar al portapapeles
        </button>
        """
    )

    if st.button(
        "Generar nueva versión",
        use_container_width=True,
        key="generate_new_version",
    ):
        st.session_state.pop("result", None)
        st.session_state["stage"] = "selection"
        st.rerun()


def _render_quality(result: dict) -> None:
    """Renderiza información de calidad cuando existe."""
    quality = result.get("evaluacion_calidad") or {}
    score = quality.get("fidelidad_score")

    if score is None:
        return

    st.html(
        f"""
        <div class="nm-result-info">
            <strong>Fidelidad:</strong> {score:.0%}
        </div>
        """
    )


def render() -> None:
    """Renderiza la pantalla completa de resultados."""
    result = st.session_state.get("result")

    if not result:
        st.session_state["stage"] = "selection"
        st.rerun()
        return

    _render_styles()
    _render_header()

    markdown = _get_markdown(result)

    # ---------------------------------------------------------
    # Estado del resultado
    # ---------------------------------------------------------
    status = result.get("status", "")

    if status == "ERROR":
        st.error("La generación terminó con error.")
    elif status == "PARTIAL":
        st.warning("Resultado parcial (sin validación de fidelidad).")
    elif status == "NO_CONTEXT":
        st.warning("No hay contexto suficiente en el documento.")

    # ---------------------------------------------------------
    # Layout principal
    # ---------------------------------------------------------
    main_col, side_col = st.columns([3.4, 1.35], gap="small")

    with main_col:
        _render_toolbar()

        tab_preview, tab_markdown = st.tabs(
            ["Vista previa", "Markdown"]
        )

        with tab_preview:
            _render_preview(markdown)

        with tab_markdown:
            _render_markdown_view(markdown)

    with side_col:
        _render_config_panel(result)
        _render_actions(result, markdown)
        _render_quality(result)

    # ---------------------------------------------------------
    # Información adicional / trazabilidad
    # ---------------------------------------------------------
    meta = result.get("metadatos") or {}
    sources = meta.get("sources", [])

    if sources:
        with st.expander(f"Fuentes ({len(sources)})"):
            for source in sources:
                page = (
                    f" · pág. {source['page']}"
                    if source.get("page") is not None
                    else ""
                )

                st.write(
                    f"`{source.get('chunk_id', '—')}`{page}"
                )

    storage = result.get("almacenamiento_oci")

    if storage:
        st.caption(
            f"Guardado en `{storage.get('bucket', '—')}` → "
            f"`{storage.get('object_name_json', '—')}`"
        )

    # ---------------------------------------------------------
    # Información de conceptos clave
    # ---------------------------------------------------------
    content = _get_content(result)
    concepts = content.get("conceptos_clave", [])

    if concepts:
        with st.expander("Conceptos clave"):
            st.write(", ".join(concepts))

    estimated_time = content.get("tiempo_estimado_min")

    if estimated_time:
        st.caption(
            f"Tiempo estimado de lectura: {estimated_time} min"
        )

    # ---------------------------------------------------------
    # JSON completo para trazabilidad
    # ---------------------------------------------------------
    with st.expander("Ver respuesta técnica"):
        st.code(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            ),
            language="json",
        )

    # ---------------------------------------------------------
    # Acción para subir otro documento
    # ---------------------------------------------------------
    if st.button(
        "Subir otro documento",
        use_container_width=True,
        key="upload_another_document",
    ):
        for key in ("ingest", "job_id", "result"):
            st.session_state.pop(key, None)

        st.session_state["stage"] = "upload"
        st.rerun()
