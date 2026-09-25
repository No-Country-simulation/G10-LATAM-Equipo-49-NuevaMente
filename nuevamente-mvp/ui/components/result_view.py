import json
import streamlit as st


def render_result():
    result = st.session_state["result"]

    if result["status"] == "NO_CONTEXT":
        st.warning("No se encontró contexto suficiente en el documento para esta consulta.")
        return

    score = result["evaluacion_calidad"]["fidelity_score"]
    if score is not None:
        st.metric("Fidelidad estimada", f"{score * 100:.0f}%")
        if score < 0.75:
            st.error("Advertencia: soporte bajo en la fuente. Revisa el contenido con cuidado.")
        elif score < 0.90:
            st.warning("Soporte moderado — se recomienda revisar antes de usarlo.")
        else:
            st.success("Soporte alto en la fuente.")
    else:
        st.info("No fue posible calcular un score de fidelidad para esta generación.")

    contenido = result.get("contenido_adaptado")
    if contenido:
        st.subheader(contenido["titulo"])
        st.write(contenido["cuerpo"])
        st.write("**Conceptos clave:**", ", ".join(contenido["conceptos_clave"]))
        st.write("**Prerrequisitos:**", ", ".join(contenido["prerrequisitos"]))

    st.write("**Fuentes utilizadas:**")
    for source in result["metadatos"]["sources"]:
        page = f" — página {source['page']}" if source.get("page") else ""
        st.write(f"- {source['chunk_id']}{page}")

    no_soportados = result["evaluacion_calidad"]["claims_no_soportados"]
    if no_soportados:
        st.write("**⚠ Claims no sustentados:**")
        for claim in no_soportados:
            st.write(f"- {claim}")

    st.download_button(
        "Descargar JSON", data=json.dumps(result, ensure_ascii=False, indent=2),
        file_name="resultado_nuevamente.json", mime="application/json",
    )

    if st.button("Probar con otro perfil sobre el mismo documento"):
        st.session_state["step"] = "configuration"
        st.rerun()
