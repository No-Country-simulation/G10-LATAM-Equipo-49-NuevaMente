"""Estado de la copia auditada y sanidad del pipeline de ingesta.

Estos controles usan los documentos demo reales de `docs/documentos_demo/`.
La premisa de infraestructura (EC2 + Docker + n8n) se asume correcta: lo que
se audita acá es el código de la aplicación.

IMPORTANTE: `test_la_copia_actual_no_puede_generar_contenido` documenta el
estado del código en esta rama. **Debe retirarse** (o invertirse) cuando se
implemente `GenerationOrchestrator.generate_content`.
"""
import pytest

from .conftest import ATLAS, HELIOS, ORION, ingestar

PERFIL = "Principiante / Transición de Carrera"
FORMATO = "Guía Práctica Paso a Paso (Tutorial)"


def test_health_responde_ok(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("documento", [ATLAS, HELIOS, ORION], ids=lambda p: p.name)
def test_los_documentos_demo_se_ingestan(client, documento) -> None:
    """La ingesta (extracción → chunks → embeddings mock → índice) funciona."""
    document_id = ingestar(client, documento)
    assert document_id.startswith("doc_")


# CAMBIO H-01/H-02/H-03 INICIO — 2026-10-24
def test_la_copia_puede_generar_contenido_en_modo_mock(client) -> None:
    """La configuración mock entrega resultado visible como modo degradado."""
    document_id = ingestar(client, ATLAS)

    accepted = client.post(
        "/adapt",
        json={
            "document_id": document_id,
            "perfil": PERFIL,
            "formato": FORMATO,
            "nicho": "Fintech",
        },
    )
    assert accepted.status_code == 202

    result = client.get(f"/adapt/{accepted.json()['job_id']}")
    assert result.status_code == 200
    assert result.json()["generation_mode"] == "mock"
    assert result.json()["status"] == "PARTIAL"
# CAMBIO H-01/H-02/H-03 FIN — 2026-10-24
