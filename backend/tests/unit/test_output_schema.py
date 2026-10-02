"""Tests del esquema de salida (QA-002, contrato NuevaMenteOutput).

Validan que instancias válidas pasan y que el `status` respeta literales.
"""
from src.output.schema import (
    AlmacenamientoOCI,
    ContenidoAdaptado,
    EvaluacionCalidad,
    ItemFlashcard,
    Metadatos,
    NuevaMenteOutput,
)


def test_output_valido_success():
    out = NuevaMenteOutput(
        status="SUCCESS",
        metadatos=Metadatos(
            doc_id="d1",
            perfil="developer",
            formato="tutorial",
            nivel_detalle="estandar",
        ),
        contenido_adaptado=ContenidoAdaptado(
            cuerpo="texto",
            items=[ItemFlashcard(frente="q", dorso="a", pista_didactica="p")],
        ),
        evaluacion_calidad=EvaluacionCalidad(fidelidad_score=0.95),
        almacenamiento_oci=AlmacenamientoOCI(bucket="b"),
    )
    assert out.status == "SUCCESS"
    assert len(out.contenido_adaptado.items) == 1


def test_output_contenido_opcional_para_error():
    out = NuevaMenteOutput(
        status="NO_CONTEXT",
        metadatos=Metadatos(
            doc_id="d1", perfil="x", formato="tutorial", nivel_detalle="estandar"
        ),
        evaluacion_calidad=EvaluacionCalidad(),
        almacenamiento_oci=None,
    )
    assert out.contenido_adaptado is None


def test_fidelidad_score_default_none():
    # VAL-005: el score puede quedar None; el rango se fuerza en implementación.
    assert EvaluacionCalidad().fidelidad_score is None
    assert EvaluacionCalidad(fidelidad_score=0.9).fidelidad_score == 0.9