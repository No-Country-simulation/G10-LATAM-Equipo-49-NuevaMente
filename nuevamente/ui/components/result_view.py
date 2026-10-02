"""Pantalla 4 — result_view (UX-001): mostrar el resultado y su trazabilidad."""
import json

import streamlit as st

_STATUS_LABEL = {
    "SUCCESS": ("success", "Resultado validado"),
    "PARTIAL": ("warning", "Resultado parcial (sin validación de fidelidad)"),
    "NO_CONTEXT": ("warning", "No hay contexto suficiente en el documento"),
    "ERROR": ("error", "La generación terminó con error"),
}


def render() -> None:
    result = st.session_state.get("result")
    if not result:
        st.session_state["stage"] = "selection"
        st.rerun()
        return

    st.header("4. Resultado")
    level, label = _STATUS_LABEL.get(result.get("status", ""), ("info", result.get("status", "")))
    getattr(st, level)(label)

    meta = result.get("metadatos", {})
    st.caption(
        f"Perfil: **{meta.get('perfil', '—')}** · Formato: **{meta.get('formato', '—')}** · "
        f"Detalle: **{meta.get('nivel_detalle', '—')}** · Documento: `{meta.get('doc_id', '—')}`"
    )

    content = result.get("contenido_adaptado")
    if content:
        st.markdown(content.get("cuerpo", ""))
        if content.get("conceptos_clave"):
            st.markdown("**Conceptos clave:** " + ", ".join(content["conceptos_clave"]))
        if content.get("tiempo_estimado_min"):
            st.caption(f"Tiempo estimado de lectura: {content['tiempo_estimado_min']} min")

    quality = result.get("evaluacion_calidad", {})
    score = quality.get("fidelidad_score")
    st.metric("Fidelidad", "No evaluada" if score is None else f"{score:.0%}")
    for note in quality.get("observaciones", []):
        st.info(note)

    sources = meta.get("sources", [])
    if sources:
        with st.expander(f"Fuentes ({len(sources)})"):
            for src in sources:
                page = f" · pág. {src['page']}" if src.get("page") is not None else ""
                st.write(f"`{src['chunk_id']}`{page}")

    storage = result.get("almacenamiento_oci")
    if storage:
        st.caption(f"Guardado en `{storage.get('bucket')}` → `{storage.get('object_name_json')}`")

    st.download_button(
        "Descargar JSON",
        data=json.dumps(result, ensure_ascii=False, indent=2),
        file_name="resultado_nuevamente.json",
        mime="application/json",
    )

    col_repeat, col_new = st.columns(2)
    if col_repeat.button("Probar otro perfil/formato", type="primary"):
        st.session_state.pop("result", None)
        st.session_state["stage"] = "selection"
        st.rerun()
    if col_new.button("Subir otro documento"):
        for key in ("ingest", "job_id", "result"):
            st.session_state.pop(key, None)
        st.session_state["stage"] = "upload"
        st.rerun()
