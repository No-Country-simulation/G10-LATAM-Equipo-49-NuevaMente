"""
NuevaMente G10 · schemas.py
Contrato estricto del Hackathon: todo JSON que salga del sistema cumple este esquema.
"""
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator

# ───────────── 1. ENUMS (Literales) ─────────────
PerfilDestinatario = Literal["Principiante", "Junior", "Arquitecto", "Ejecutivo"]
FormatoSalida      = Literal["Tutorial", "Flashcards", "Quiz", "TLDR", "Guion"]
NichoSector        = Literal["Fintech", "Salud", "E-commerce", "General"]
NivelDetalle       = Literal["Didactico", "Tecnico", "Estrategico"]

# ───────────── 2. ENTRADA (Solicitud) ─────────────
class SolicitudAdaptacion(BaseModel):
    """Payload que recibe el webhook de n8n / la UI de Streamlit."""
    documento_titulo: str = Field(..., min_length=3, description="Título del documento técnico")
    documento_contenido: str = Field(..., min_length=50, description="Texto extraído del PDF/MD/TXT")
    perfil_destinatario: PerfilDestinatario
    formato_salida: FormatoSalida
    nicho_sector: NichoSector = "General"
    nivel_detalle: NivelDetalle = "Didactico"

# ───────────── 3. ITEMS POR FORMATO PEDAGÓGICO ─────────────
class ItemFlashcard(BaseModel):
    tipo: Literal["flashcard"] = "flashcard"
    frente: str = Field(..., min_length=5)
    dorso: str = Field(..., min_length=5)
    pista_didactica: str

class ItemQuiz(BaseModel):
    tipo: Literal["quiz"] = "quiz"
    pregunta: str
    opciones: list[str] = Field(..., min_length=2, max_length=5)
    respuesta_correcta: str
    justificacion: str

class ItemTutorial(BaseModel):
    tipo: Literal["tutorial"] = "tutorial"
    paso: int = Field(..., ge=1)
    titulo_paso: str
    instrucciones: str
    codigo_ejemplo: Optional[str] = None

class ItemResumen(BaseModel):   # TL;DR
    tipo: Literal["resumen"] = "resumen"
    punto_clave: str
    detalle: str

class ItemGuion(BaseModel):     # Guion de clase/video
    tipo: Literal["guion"] = "guion"
    seccion: str
    narracion: str
    apoyo_visual: Optional[str] = None

ItemContenido = Union[ItemFlashcard, ItemQuiz, ItemTutorial, ItemResumen, ItemGuion]

# ───────────── 4. BLOQUES DE SALIDA ─────────────
class Metadatos(BaseModel):
    perfil_aplicado: PerfilDestinatario
    formato_generado: FormatoSalida
    tiempo_estimado_estudio_minutos: int = Field(..., ge=1, le=240)
    conceptos_clave: list[str] = Field(..., min_length=1)

class ContenidoAdaptado(BaseModel):
    titulo: str
    introduccion_contextualizada: str
    items: list[ItemContenido] = Field(..., min_length=1)

class EvaluacionCalidad(BaseModel):
    anclaje_fuente_score: float = Field(..., ge=0.0, le=1.0)  # ← lo lee el IF de n8n
    claridad_pedagogica: Literal["Alta", "Media", "Baja"]
    observaciones: str

class AlmacenamientoOCI(BaseModel):
    bucket: str
    objeto_id: str
    status_upload: Literal["completado", "pendiente", "error"]

# ───────────── 5. PAQUETE FINAL (Salida de la API) ─────────────
class PaqueteEducativo(BaseModel):
    status: Literal["exito", "error"]
    metadatos: Metadatos
    contenido_adaptado: ContenidoAdaptado
    evaluacion_calidad: EvaluacionCalidad
    almacenamiento_oci: AlmacenamientoOCI

    @model_validator(mode="after")
    def validar_coherencia_formato(self):
        """Los items deben corresponder al formato declarado (anti-JSON frankenstein)."""
        mapa = {
            "Flashcards": ItemFlashcard, "Quiz": ItemQuiz,
            "Tutorial": ItemTutorial, "TLDR": ItemResumen, "Guion": ItemGuion,
        }
        clase_esperada = mapa[self.metadatos.formato_generado]
        for i, item in enumerate(self.contenido_adaptado.items):
            if not isinstance(item, clase_esperada):
                raise ValueError(
                    f"items[{i}] es '{item.tipo}' pero el formato declarado "
                    f"es '{self.metadatos.formato_generado}'"
                )
        return self

# ───────────── 6. ERROR AMIGABLE (Checklist del Hackathon) ─────────────
class RespuestaError(BaseModel):
    status: Literal["error"] = "error"
    codigo: str                        # ej. "OCI_UPLOAD_FAIL", "LLM_TIMEOUT"
    mensaje_amigable: str              # lo que ve el usuario en Streamlit
    detalle_tecnico: Optional[str] = None   # solo logs / Discord del equipo