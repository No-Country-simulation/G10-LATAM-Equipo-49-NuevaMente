"""
NuevaMente G10 · main.py · Demo base (Fase 1)
Corre con: uvicorn main:app --reload --port 8000
"""
import re
from collections import Counter
from fastapi import FastAPI, HTTPException, Query

from schemas import (
    SolicitudAdaptacion, PaqueteEducativo, Metadatos, ContenidoAdaptado,
    EvaluacionCalidad, AlmacenamientoOCI, RespuestaError, ListadoOCI,
    ItemFlashcard, ItemQuiz, ItemTutorial, ItemResumen, ItemGuion,
)
from services.oci_storage import OciStorageService

app = FastAPI(title="NuevaMente G10", version="0.1.0-demo",
              description="Demo base Hackathon ONE G10 · RAG naive + generador placeholder")

oci_service = OciStorageService()

STOP = {"de","la","el","en","y","a","los","del","se","las","por","un","una","que",
        "con","para","su","es","son","o","como","mas","entre","sobre","este","esta",
        "the","of","and","in","to","is","are","it","that","this"}

def chunk_text(texto: str, size: int = 400) -> list[str]:
    frags = re.split(r"(?<=[.!?])\s+", texto)
    chunks, actual = [], ""
    for f in frags:
        if len(actual) + len(f) > size and actual:
            chunks.append(actual.strip()); actual = f
        else:
            actual += " " + f
    if actual.strip(): chunks.append(actual.strip())
    return chunks or [texto]

def tokens(texto: str) -> set[str]:
    return set(re.findall(r"\w+", texto.lower()))

def retrieve(chunks: list[str], query: str, k: int = 3) -> list[str]:
    q = tokens(query)
    return [c for _, c in sorted(((len(q & tokens(c)), c) for c in chunks),
                                 reverse=True, key=lambda x: x[0])[:k]]

def conceptos_clave(texto: str, n: int = 4) -> list[str]:
    freq = Counter(w for w in re.findall(r"[A-Za-zÁ-ú]{4,}", texto.lower()) if w not in STOP)
    return [w for w, _ in freq.most_common(n)] or ["concepto"]

def anclaje_score(gen: str, fuentes: list[str]) -> float:
    src, g = tokens(" ".join(fuentes)), tokens(gen)
    return round(min(1.0, len(src & g) / max(1, len(g))), 2)

INTROS = {
    "Principiante": "Imagina este concepto como una caja de herramientas: empezamos por lo más simple.",
    "Junior": "Este concepto se conecta con lo que ya usas en el día a día del desarrollo.",
    "Arquitecto": "Analicemos el concepto desde el diseño, los trade-offs y la escalabilidad.",
    "Ejecutivo": "En una línea: esto impacta costos, riesgos y velocidad de entrega.",
}
TITULOS = {"Flashcards": "Flashcards de memorización", "Quiz": "Quiz interactivo",
           "Tutorial": "Guía práctica paso a paso", "TLDR": "Resumen ejecutivo (TL;DR)",
           "Guion": "Guion de clase / video"}

def _frase(c: str) -> str: return c.split(".")[0].strip()

def build_flashcards(f, p): return [
    ItemFlashcard(frente=f"¿Qué dice el documento sobre: {_frase(c)[:70]}...?",
                  dorso=c[:280], pista_didactica=f"Repasa el fragmento {i+1} de la fuente.")
    for i, c in enumerate(f[:3])]

def build_quiz(f, p):
    items = []
    for i, c in enumerate(f[:2]):
        correcta = _frase(c)[:90]
        dist = [_frase(x)[:90] for j, x in enumerate(f) if j != i and _frase(x)[:90] != correcta][:2]
        while len(dist) < 2: dist.append("Ninguna de las anteriores")
        items.append(ItemQuiz(pregunta=f"Según la fuente, ¿cuál afirmación es correcta sobre: {correcta[:50]}...?",
                              opciones=[correcta] + dist, respuesta_correcta=correcta,
                              justificacion=f"Anclada literalmente en el fragmento {i+1} del documento."))
    return items

def build_tutorial(f, p): return [
    ItemTutorial(paso=i+1, titulo_paso=f"Comprende: {_frase(c)[:60]}",
                 instrucciones=c[:250], codigo_ejemplo=None) for i, c in enumerate(f[:3])]

def build_tldr(f, p): return [
    ItemResumen(punto_clave=_frase(c)[:80], detalle=c[:200]) for c in f[:3]]

def build_guion(f, p): return [
    ItemGuion(seccion=f"Escena {i+1}", narracion=f"{INTROS[p]} {c[:200]}",
              apoyo_visual="Resaltar el fragmento en pantalla") for i, c in enumerate(f[:3])]

BUILDERS = {"Flashcards": build_flashcards, "Quiz": build_quiz, "Tutorial": build_tutorial,
            "TLDR": build_tldr, "Guion": build_guion}

# Campos que llevan contenido anclado a la fuente (las palabras de plantilla no cuentan)
CAMPOS_CONTENIDO = {"dorso", "instrucciones", "detalle", "narracion", "respuesta_correcta"}

def items_a_texto(items) -> str:
    partes = [str(v) for it in items for k, v in it.model_dump().items()
              if k in CAMPOS_CONTENIDO and isinstance(v, str)]
    return " ".join(partes)

@app.get("/health")
def health():
    return {"status": "ok", "fase": "demo-base", "vector_store": "memoria (naive)",
            "llm": "placeholder", "oci": "pendiente"}

@app.get("/test/oci/objects", response_model=ListadoOCI)
def listar_objetos_oci(
    prefix: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    start: str | None = None,
):
    try:
        return oci_service.list_objects(prefix=prefix, limit=limit, start=start)
    except Exception as e:
        raise HTTPException(502, detail=RespuestaError(
            codigo="OCI_LIST_FAIL",
            mensaje_amigable="No se pudo listar el bucket de OCI.",
            detalle_tecnico=str(e)).model_dump())

@app.post("/adaptar", response_model=PaqueteEducativo)
def adaptar(req: SolicitudAdaptacion):
    try:
        chunks = chunk_text(req.documento_contenido)
        fuentes = retrieve(chunks, f"{req.documento_titulo} {req.nicho_sector}")
        items = BUILDERS[req.formato_salida](fuentes, req.perfil_destinatario)
        score = anclaje_score(items_a_texto(items), fuentes)
        return PaqueteEducativo(
            status="exito",
            metadatos=Metadatos(perfil_aplicado=req.perfil_destinatario,
                                formato_generado=req.formato_salida,
                                tiempo_estimado_estudio_minutos=len(items) * 2 + 3,
                                conceptos_clave=conceptos_clave(req.documento_contenido)),
            contenido_adaptado=ContenidoAdaptado(
                titulo=f"{TITULOS[req.formato_salida]} · {req.documento_titulo}",
                introduccion_contextualizada=INTROS[req.perfil_destinatario], items=items),
            evaluacion_calidad=EvaluacionCalidad(
                anclaje_fuente_score=score, claridad_pedagogica="Media",
                observaciones="Demo base: anclaje por extracción directa. Fase 2: reescritura con Gemini + Agente Crítico."),
            almacenamiento_oci=AlmacenamientoOCI(
                bucket="nuevamente-contenidos-educativos",
                objeto_id=f"{req.documento_titulo[:20].lower().replace(' ', '-')}-{req.formato_salida.lower()}.json",
                status_upload="pendiente"),
        )
    except Exception as e:
        raise HTTPException(500, detail=RespuestaError(
            codigo="ERROR_INTERNO",
            mensaje_amigable="Algo falló al adaptar el contenido. El equipo ya fue notificado.",
            detalle_tecnico=str(e)).model_dump())