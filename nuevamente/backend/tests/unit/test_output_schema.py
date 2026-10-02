"""TASK-003 — schema de salida NuevaMenteOutput."""
import pytest

from src.output.schema import (
    AlmacenamientoOCI,
    ContenidoAdaptado,
    EvaluacionCalidad,
    Metadatos,
    NuevaMenteOutput,
    Source,
)


def _metadatos() -> Metadatos:
    return Metadatos(
        doc_id="doc_a",
        perfil="Principiante / Transición de Carrera",
        formato="Guía Práctica Paso a Paso (Tutorial)",
        sources=[Source(chunk_id="doc_a-chunk-0", page=7)],
    )


def test_full_instance_is_valid_and_serializable():
    output = NuevaMenteOutput(
        status="SUCCESS",
        metadatos=_metadatos(),
        contenido_adaptado=ContenidoAdaptado(
            cuerpo="texto", conceptos_clave=["a"], tiempo_estimado_min=15
        ),
        evaluacion_calidad=EvaluacionCalidad(fidelidad_score=0.93, dificultad="baja"),
        almacenamiento_oci=AlmacenamientoOCI(bucket="b", object_name_json="generated/x.json"),
    )
    dumped = output.model_dump()
    assert dumped["metadatos"]["sources"] == [{"chunk_id": "doc_a-chunk-0", "page": 7}]
    assert dumped["evaluacion_calidad"]["fidelidad_score"] == 0.93
    assert "generated/x.json" in output.model_dump_json()


def test_optional_fields_can_be_missing():
    output = NuevaMenteOutput(
        status="NO_CONTEXT", metadatos=_metadatos(), evaluacion_calidad=EvaluacionCalidad()
    )
    assert output.contenido_adaptado is None
    assert output.almacenamiento_oci is None
    assert output.evaluacion_calidad.fidelidad_score is None


@pytest.mark.parametrize("score", [-0.1, 1.5])
def test_score_out_of_range_is_rejected(score):
    with pytest.raises(ValueError):
        EvaluacionCalidad(fidelidad_score=score)


@pytest.mark.parametrize("score", [0.0, 1.0, None])
def test_score_boundaries_are_valid(score):
    assert EvaluacionCalidad(fidelidad_score=score).fidelidad_score == score
