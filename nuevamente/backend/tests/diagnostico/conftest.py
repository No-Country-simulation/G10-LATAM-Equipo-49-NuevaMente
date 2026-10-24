"""Helpers compartidos por la suite de diagnóstico.

CAMBIO H-01/H-02 INICIO — 2026-10-24
La premisa del ambiente es: flujo n8n funcionando y backend contenerizado en
Docker sobre AWS EC2. Para que la simulación no dependa de la red ni de
credenciales, se ejercita el mismo pipeline (ingesta → RAG → generación →
validación → ensamblado) con los proveedores mock, y se simulan fallos del
proveedor donde hace falta.
CAMBIO H-01/H-02 FIN — 2026-10-24
"""
from difflib import SequenceMatcher
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).resolve().parents[3] / "docs" / "documentos_demo"
ATLAS = DOCS_DIR / "atlas-pay-5p.md"
HELIOS = DOCS_DIR / "helios-rec-10p.md"
ORION = DOCS_DIR / "orion-platform-13p.md"


def ingestar(client, path: Path = ATLAS) -> str:
    """Ingesta un documento demo real y devuelve su `document_id`."""
    contenido = path.read_bytes()
    response = client.post(
        "/ingest",
        files={"file": (path.name, contenido, "text/markdown")},
    )
    assert response.status_code == 201, response.text
    return response.json()["document_id"]


def adaptar(client, document_id: str, formato: str, perfil: str) -> dict:
    """Ejecuta /adapt + polling y devuelve el JSON final del job."""
    accepted = client.post(
        "/adapt",
        json={
            "document_id": document_id,
            "perfil": perfil,
            "formato": formato,
            "nicho": "Fintech",
        },
    )
    assert accepted.status_code == 202, accepted.text
    job_id = accepted.json()["job_id"]

    result = client.get(f"/adapt/{job_id}")
    assert result.status_code == 200, result.text
    return result.json()


def cuerpo(result: dict) -> str:
    """Extrae el cuerpo generado o cadena vacía si no hubo contenido."""
    contenido = result.get("contenido_adaptado") or {}
    return contenido.get("cuerpo") or ""


def normalizar(texto: str, formato: str) -> str:
    """Quita el único texto que hoy depende del formato (el encabezado).

    Si tras normalizar dos cuerpos son iguales, entonces el formato NO tuvo
    ningún efecto sobre el contenido: solo cambió una etiqueta.
    """
    return texto.replace(formato, "<FORMATO>")


def similitud(a: str, b: str) -> float:
    """Ratio de similitud (0..1) entre dos textos."""
    return SequenceMatcher(None, a, b).ratio()


@pytest.fixture
def documento_demo(client) -> str:
    return ingestar(client)
