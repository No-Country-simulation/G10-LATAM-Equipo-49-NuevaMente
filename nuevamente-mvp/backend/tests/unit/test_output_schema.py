import pytest
from pydantic import ValidationError

from src.output.schema import NuevaMenteOutput, Metadata, QualityEvaluation, Source


def _base_metadata():
    return Metadata(doc_id="doc_1", profile="principiante", format="tutorial",
                     detail_level="estandar", sources=[Source(chunk_id="c1", page=1)])


def test_valid_output_instance():
    output = NuevaMenteOutput(
        status="SUCCESS", metadatos=_base_metadata(),
        evaluacion_calidad=QualityEvaluation(fidelity_score=0.9),
    )
    assert output.status == "SUCCESS"


def test_optional_fields_missing_still_validates():
    output = NuevaMenteOutput(
        status="NO_CONTEXT", metadatos=_base_metadata(),
        evaluacion_calidad=QualityEvaluation(),
    )
    assert output.contenido_adaptado is None


def test_fidelity_score_out_of_range_fails():
    with pytest.raises(ValidationError):
        QualityEvaluation(fidelity_score=1.5)
