"""Estilos globales de la interfaz de NuevaMente."""

import streamlit as st


def load_styles() -> None:
    """Carga los estilos visuales de NuevaMente."""

    st.markdown(
        """

<style>



/* ============================================================

   COLORES

   ============================================================ */



:root {

    --nm-blue: #0282FB;

    --nm-dark-blue: #083591;

    --nm-sidebar: #F1F8FE;

    --nm-light-blue: #D7ECFF;

    --nm-border: #D9D9D9;

    --nm-text: #111111;

    --nm-secondary: #666666;

}





/* ============================================================

   APLICACIÓN

   ============================================================ */



.stApp {

    background-color: #FFFFFF !important;

}





/* ============================================================

   SIDEBAR

   ============================================================ */



section[data-testid="stSidebar"] {

    background-color: var(--nm-sidebar) !important;

    border-right: 1px solid #DDEAF5 !important;



    width: 320px !important;

    min-width: 220px !important;

}



section[data-testid="stSidebar"] > div {

    padding-top: 22px !important;

    padding-left: 18px !important;

    padding-right: 18px !important;

}





/* ============================================================

   LOGO

   ============================================================ */



section[data-testid="stSidebar"] img {

    width: 345px !important;

    max-width: 100% !important;

    height: auto !important;



    margin-bottom: 5px !important;

}





/* ============================================================

   SEPARADOR SIDEBAR

   ============================================================ */



.sidebar-separator {

    width: 100%;

    height: 1px;



    background-color: #D8E8F5;



    margin-top: 10px;

    margin-bottom: 18px;

}





/* ============================================================

   STEPPER

   ============================================================ */



.step-item {

    display: flex;

    align-items: center;



    gap: 9px;



    min-height: 30px;



    margin-bottom: 9px;

}



.step-circle {

    width: 42px;

    height: 42px;



    min-width: 42px;



    border-radius: 50%;



    display: flex;

    align-items: center;

    justify-content: center;



    box-sizing: border-box;



    font-size: 21px;

}



.step-label {

    font-size: 22px;



    white-space: nowrap;



    line-height: 1.2;

}





/* ============================================================

   PASO ACTIVO

   ============================================================ */



.step-item.active .step-circle {

    background-color: var(--nm-blue);

    color: #FFFFFF;

    border: 1px solid var(--nm-blue);

}



.step-item.active .step-label {

    color: #111111;

    font-weight: 700;

}





/* ============================================================

   PASO COMPLETADO

   ============================================================ */



.step-item.completed .step-circle {

    background-color: var(--nm-blue);

    color: #FFFFFF;

    border: 1px solid var(--nm-blue);

}



.step-item.completed .step-label {

    color: #111111;

    font-weight: 500;

}





/* ============================================================

   PASO INACTIVO

   ============================================================ */



.step-item.inactive .step-circle {

    background-color: #DCE7F0;

    color: #263746;

    border: 1px solid #DCE7F0;

}



.step-item.inactive .step-label {

    color: #111111;

    font-weight: 400;

}





/* ============================================================

   CONTENIDO PRINCIPAL

   ============================================================ */



[data-testid="stMainBlockContainer"] {

    width: 100% !important;

    max-width: 1280px !important;



    margin-left: 0 !important;

    margin-right: 0 !important;



    padding-top: 34px !important;

    padding-left: 42px !important;

    padding-right: 55px !important;

    padding-bottom: 45px !important;



    box-sizing: border-box !important;

}



.main .block-container {

    width: 100%;

    max-width: 1280px;



    margin-left: 0;

    margin-right: 0;



    padding-top: 34px;

    padding-left: 42px;

    padding-right: 55px;

    padding-bottom: 45px;



    box-sizing: border-box;

}





/* ============================================================

   TÍTULO

   ============================================================ */



h1 {

    color: var(--nm-text) !important;



    font-size: 30px !important;



    font-weight: 500 !important;



    line-height: 1.2 !important;



    margin-top: 0 !important;

    margin-bottom: 8px !important;

}





/* ============================================================

   TÍTULO PERSONALIZADO

   ============================================================ */



.nm-page-title {

    color: var(--nm-text);



    font-size: 30px;

    font-weight: 500;



    line-height: 1.2;



    margin-top: 0;

    margin-bottom: 8px;

}



.nm-page-description {

    color: var(--nm-text);



    font-size: 24px;



    line-height: 1.4;



    margin-bottom: 14px;

}





/* ============================================================

   TEXTO GENERAL

   ============================================================ */



.stMarkdown p {

    color: var(--nm-text);



    font-size: 22px;



    line-height: 1.4;

}





/* ============================================================

   TARJETA PRINCIPAL DEL UPLOAD

   ============================================================ */



[data-testid="stVerticalBlockBorderWrapper"] {

    width: 100% !important;



    box-sizing: border-box !important;



    border: 1px solid var(--nm-border) !important;



    border-radius: 6px !important;



    background-color: #FFFFFF !important;



    box-shadow: none !important;



    min-height: 205px;



    padding: 12px !important;

}





/* ============================================================

   FILE UPLOADER

   ============================================================ */



[data-testid="stFileUploader"] {

    width: 100% !important;



    background: transparent !important;



    box-shadow: none !important;



    margin: 0 !important;



    padding: 0 !important;

}





/* ============================================================

   ZONA DEL UPLOADER

   ============================================================ */



[data-testid="stFileUploaderDropzone"] {

    position: relative !important;



    width: 100% !important;



    height: 30px !important;

    min-height: 30px !important;



    padding: 0 !important;

    margin: 0 !important;



    background: transparent !important;



    border: none !important;



    box-shadow: none !important;



    border-radius: 0 !important;



    box-sizing: border-box !important;

}





/* ============================================================

   CONTENEDOR INTERNO DEL UPLOADER

   ============================================================ */



[data-testid="stFileUploaderDropzone"] > div {

    width: 100% !important;

    height: 100% !important;



    margin: 0 !important;

    padding: 0 !important;



    box-sizing: border-box !important;

}





/* ============================================================

   OCULTAR TEXTOS NATIVOS

   ============================================================ */



[data-testid="stFileUploaderDropzone"] small {

    display: none !important;

}



[data-testid="stFileUploaderDropzoneInstructions"] {

    display: none !important;

}





/* ============================================================

   BOTÓN REAL DE STREAMLIT

   ============================================================ */



[data-testid="stFileUploaderDropzone"] button {

    position: absolute !important;



    left: 50% !important;

    top: 50% !important;



    transform: translate(-50%, -50%) !important;



    width: 120px !important;

    min-width: 120px !important;

    max-width: 120px !important;



    height: 30px !important;

    min-height: 30px !important;



    margin: 0 !important;

    padding: 0 !important;



    background-color: var(--nm-blue) !important;



    color: transparent !important;



    border: none !important;



    border-radius: 5px !important;



    box-shadow: none !important;



    overflow: hidden !important;



    font-size: 0 !important;



    line-height: 1 !important;

}





/* ============================================================

   OCULTAR CONTENIDO NATIVO DEL BOTÓN

   ============================================================ */



[data-testid="stFileUploaderDropzone"] button span {

    display: none !important;

}



[data-testid="stFileUploaderDropzone"] button svg {

    display: none !important;

}



[data-testid="stFileUploaderDropzone"] button::before {

    display: none !important;



    content: none !important;

}





/* ============================================================

   TEXTO PERSONALIZADO DEL BOTÓN

   ============================================================ */



[data-testid="stFileUploaderDropzone"] button::after {

    content: "Seleccionar archivo";



    position: absolute !important;



    left: 50% !important;

    top: 50% !important;



    transform: translate(-50%, -50%) !important;



    display: block !important;



    width: 100% !important;



    margin: 0 !important;

    padding: 0 !important;



    color: #FFFFFF !important;



    font-family: Arial, sans-serif !important;



    font-size: 12px !important;



    font-weight: 500 !important;



    line-height: 1 !important;



    text-align: center !important;



    white-space: nowrap !important;



    pointer-events: none !important;

}





/* ============================================================

   HOVER DEL BOTÓN UPLOAD

   ============================================================ */



[data-testid="stFileUploaderDropzone"] button:hover {

    background-color: var(--nm-blue) !important;



    opacity: 0.78 !important;



    transform: translate(-50%, -50%) !important;

}





/* ============================================================

   CLICK DEL BOTÓN UPLOAD

   ============================================================ */



[data-testid="stFileUploaderDropzone"] button:active {

    transform: translate(-50%, -50%) scale(0.98) !important;

}





/* ============================================================

   ICONO GRANDE DE SUBIDA

   ============================================================ */



.nm-upload-icon {

    width: 70px;

    height: 70px;



    margin: 6px auto 10px auto;



    border-radius: 50%;



    background-color: var(--nm-light-blue);



    color: var(--nm-blue);



    display: flex;



    align-items: center;

    justify-content: center;



    font-size: 48px;



    line-height: 1;



    font-weight: 300;

}





/* ============================================================

   TEXTO DEL UPLOAD

   ============================================================ */



.nm-upload-title {

    text-align: center;



    color: var(--nm-text);



    font-size: 24px;



    font-weight: 700;



    margin-top: 5px;

}



.nm-upload-subtitle {

    text-align: center;



    color: var(--nm-secondary);



    font-size: 24px;



    margin-top: 3px;



    margin-bottom: 7px;

}





/* ============================================================

   ESTADO DE ÉXITO

   ============================================================ */



.nm-success-icon {

    width: 70px;

    height: 70px;



    margin: 6px auto 10px auto;



    border-radius: 50%;



    background-color: #D9FFE0;



    color: #24D44B;



    display: flex;



    align-items: center;

    justify-content: center;



    font-size: 45px;



    font-weight: 700;



    line-height: 1;

}





.nm-success-title {

    text-align: center;



    color: #111111;



    font-size: 24px;



    font-weight: 700;



    margin-top: 4px;

}





.nm-file-name {
    text-align: center;
    color: #777777;
    font-size: 15px;
    margin-top: 10px;
    margin-bottom: 20px;
}





/* ============================================================

   BOTÓN ARCHIVO SELECCIONADO

   ============================================================ */



.nm-selected-file-button {

    width: 125px;



    height: 30px;



    margin: 12px auto 0 auto;



    display: flex;



    align-items: center;

    justify-content: center;



    background-color: #24D44B;



    color: #FFFFFF;



    border-radius: 5px;



    font-size: 9px;



    font-weight: 500;

}





/* ============================================================

   RECOMENDACIONES

   ============================================================ */



.nm-recommendations {

    width: 100%;



    margin-top: 16px;



    padding: 12px 16px;



    box-sizing: border-box;



    display: flex;



    align-items: center;



    gap: 12px;



    background-color: #D6EAFF;



    border-radius: 7px;

}





.nm-recommendations-icon {

    width: 28px;



    min-width: 28px;



    font-size: 22px;



    text-align: center;

}





.nm-recommendations-content {

    flex: 1;

}





.nm-recommendations-title {

    color: var(--nm-text);



    font-size: 21px;



    font-weight: 700;



    margin-bottom: 4px;

}





.nm-recommendations-text {

    color: var(--nm-text);



    font-size: 20px;



    line-height: 1.45;

}





/* ============================================================

   BOTÓN SIGUIENTE

   ============================================================ */



.nm-next-row {

    width: 100%;



    display: flex;



    justify-content: flex-end;



    margin-top: 18px;

}





div.stButton > button {

    background-color: #75B9FA !important;



    color: #FFFFFF !important;



    border: none !important;



    border-radius: 6px !important;



    min-height: 38px !important;



    font-size: 11px !important;



    font-weight: 500 !important;



    transition:

        background-color 0.2s ease,

        opacity 0.2s ease;

}





div.stButton > button:hover {

    background-color: var(--nm-blue) !important;



    color: #FFFFFF !important;

}





div.stButton > button:disabled {

    background-color: #75B9FA !important;



    color: #FFFFFF !important;



    opacity: 0.65 !important;

}





/* ============================================================

   PANTALLAS GRANDES

   ============================================================ */



@media (min-width: 1400px) {



    [data-testid="stMainBlockContainer"] {

        max-width: 1380px !important;



        padding-left: 48px !important;

        padding-right: 70px !important;

    }



    .main .block-container {

        max-width: 1380px;



        padding-left: 48px;

        padding-right: 70px;

    }

}





/* ============================================================

   LAPTOP

   ============================================================ */



@media (max-width: 1200px) {



    section[data-testid="stSidebar"] {

        width: 205px !important;

        min-width: 205px !important;

    }



    [data-testid="stMainBlockContainer"] {

        max-width: 100% !important;



        padding-left: 35px !important;

        padding-right: 35px !important;

    }



    .main .block-container {

        max-width: 100%;



        padding-left: 35px;

        padding-right: 35px;

    }

}





/* ============================================================

   TABLET

   ============================================================ */



@media (max-width: 900px) {



    section[data-testid="stSidebar"] {

        width: 190px !important;

        min-width: 190px !important;

    }



    section[data-testid="stSidebar"] > div {

        padding-left: 15px !important;

        padding-right: 15px !important;

    }



    section[data-testid="stSidebar"] img {

        width: 135px !important;

    }



    [data-testid="stMainBlockContainer"] {

        padding-left: 25px !important;

        padding-right: 25px !important;

        padding-top: 28px !important;

    }



    .main .block-container {

        padding-left: 25px;

        padding-right: 25px;

        padding-top: 28px;

    }



    h1 {

        font-size: 27px !important;

    }



    .nm-page-title {

        font-size: 27px;

    }



    .nm-upload-icon,

    .nm-success-icon {

        width: 64px;

        height: 64px;



        font-size: 44px;

    }

}





/* ============================================================

   MÓVIL

   ============================================================ */



@media (max-width: 600px) {



    section[data-testid="stSidebar"] {

        width: 250px !important;

        min-width: 250px !important;

    }



    section[data-testid="stSidebar"] > div {

        padding-left: 18px !important;

        padding-right: 18px !important;

    }



    section[data-testid="stSidebar"] img {

        width: 145px !important;

    }



    [data-testid="stMainBlockContainer"] {

        max-width: 100% !important;



        padding-left: 14px !important;

        padding-right: 14px !important;

        padding-top: 22px !important;

    }



    .main .block-container {

        max-width: 100%;



        padding-left: 14px;

        padding-right: 14px;

        padding-top: 22px;

    }



    h1 {

        font-size: 23px !important;

    }



    .nm-page-title {

        font-size: 23px;

    }



    .stMarkdown p {

        font-size: 10px;

    }



    [data-testid="stVerticalBlockBorderWrapper"] {

        min-height: 180px;



        padding: 9px !important;

    }



    .nm-upload-icon,

    .nm-success-icon {

        width: 58px;

        height: 58px;



        font-size: 39px;



        margin-top: 4px;

    }



    .nm-upload-title {

        font-size: 12px;

    }



    .nm-upload-subtitle {

        font-size: 8px;

    }



    [data-testid="stFileUploaderDropzone"] {

        height: 30px !important;

        min-height: 30px !important;

    }



    .nm-recommendations {

        margin-top: 13px;



        padding: 10px 12px;



        gap: 8px;

    }



    .nm-recommendations-title {

        font-size: 10px;

    }



    .nm-recommendations-text {

        font-size: 8px;

    }



    div.stButton > button {

        min-height: 38px !important;



        font-size: 10px !important;

    }

}





/* ============================================================

   MÓVIL PEQUEÑO

   ============================================================ */



@media (max-width: 420px) {



    [data-testid="stMainBlockContainer"] {

        padding-left: 9px !important;

        padding-right: 9px !important;

    }



    .main .block-container {

        padding-left: 9px;

        padding-right: 9px;

    }



    h1 {

        font-size: 21px !important;

    }



    .nm-page-title {

        font-size: 21px;

    }



    .nm-upload-title {

        font-size: 11px;

    }



    .nm-upload-subtitle {

        font-size: 8px;

    }



    .nm-selected-file-button {

        width: 120px;

    }



    [data-testid="stFileUploaderDropzone"] button {

        width: 120px !important;

        min-width: 120px !important;

        max-width: 120px !important;

    }

}



</style>

        """,
        unsafe_allow_html=True,
    )
