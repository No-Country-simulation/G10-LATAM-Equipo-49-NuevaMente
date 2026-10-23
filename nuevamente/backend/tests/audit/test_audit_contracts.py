"""AUD-005, 006, 015, 016, 019 — dependencias, contrato UI/backend, lint y logging."""
import ast
import io
import logging
import re
import shutil
import subprocess
import sys

import pytest

from src.core.exceptions import InvalidFileError
from src.core.logging import get_logger
from src.ingestion.validators import detect_type
from tests.audit._support import REPO_ROOT

_IMPORT_A_PAQUETE = {
    "google": "google-genai",
    "pydantic_settings": "pydantic-settings",
    "langchain_text_splitters": "langchain-text-splitters",
    "multipart": "python-multipart",
}
_PROPIOS = {"src", "tests", "api_client", "components"}


def _requirements() -> str:
    textos = [
        p.read_text(encoding="utf-8")
        for p in (REPO_ROOT / "backend").glob("requirements*.txt")
    ]
    return "\n".join(textos).lower()


def _imports_de_produccion() -> set[str]:
    encontrados: set[str] = set()
    for base in (REPO_ROOT / "backend" / "src", REPO_ROOT / "ui"):
        for ruta in base.rglob("*.py"):
            for nodo in ast.walk(ast.parse(ruta.read_text(encoding="utf-8"))):
                if isinstance(nodo, ast.Import):
                    encontrados.update(a.name.split(".")[0] for a in nodo.names)
                elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0 and nodo.module:
                    encontrados.add(nodo.module.split(".")[0])
    return {m for m in encontrados if m not in sys.stdlib_module_names and m not in _PROPIOS}


# REGRESIÓN PERMANENTE — AUD-005 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_005_toda_dependencia_importada_esta_declarada():
    declarado = _requirements()
    faltan = sorted(m for m in _imports_de_produccion()
                    if _IMPORT_A_PAQUETE.get(m, m).lower().replace("_", "-") not in declarado)
    assert faltan == []


# REGRESIÓN PERMANENTE — AUD-006 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_006_python_multipart_esta_declarado_si_hay_subida_de_archivos():
    main = (REPO_ROOT / "backend" / "src" / "api" / "main.py").read_text(encoding="utf-8")
    assert "UploadFile" in main  # precondición: el endpoint /ingest usa multipart
    assert "python-multipart" in _requirements()


def _tipos_ofrecidos_por_la_ui() -> list[str]:
    fuente = (REPO_ROOT / "ui" / "components" / "upload_view.py").read_text(encoding="utf-8")
    bloque = re.search(r"type=\[(.*?)\]", fuente, re.S).group(1)
    return re.findall(r'"([a-z]+)"', bloque)


# REGRESIÓN PERMANENTE — AUD-015 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_015_la_ui_solo_ofrece_formatos_que_el_backend_acepta():
    rechazados = []
    for extension in _tipos_ofrecidos_por_la_ui():
        try:
            detect_type(f"archivo.{extension}")
        except InvalidFileError:
            rechazados.append(extension)
    assert rechazados == []


# REGRESIÓN PERMANENTE — AUD-016 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_016_ruff_no_reporta_errores():
    if shutil.which("ruff") is None:
        pytest.skip("ruff no está instalado (pip install -r requirements-dev.txt)")
    resultado = subprocess.run(
        ["ruff", "check", "--config", "pyproject.toml", "src", "tests", "../ui"],
        cwd=REPO_ROOT / "backend", capture_output=True, text=True,
    )
    assert resultado.returncode == 0, resultado.stdout[-500:]


# REGRESIÓN PERMANENTE — AUD-019 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_019_un_evento_de_log_ocupa_una_sola_linea():
    salida = io.StringIO()
    manejador = logging.StreamHandler(salida)
    registro = logging.getLogger("aud.contratos")
    registro.handlers, registro.propagate = [manejador], False
    registro.setLevel(logging.INFO)
    get_logger("aud.contratos").info("pipeline_stage", filename="x.md\nERROR\tfake=1")
    assert len(salida.getvalue().strip().splitlines()) == 1


# ------------------------------------------------------------ controles positivos
@pytest.mark.parametrize("nombre", ["informe.docx", "datos.exe", "sinextension", ""])
def test_ok_el_backend_rechaza_formatos_no_soportados(nombre):
    with pytest.raises(InvalidFileError):
        detect_type(nombre)


def test_ok_el_storage_mock_bloquea_path_traversal(tmp_path):
    from src.core.exceptions import StorageError
    from src.storage.mock_client import MockStorageClient

    with pytest.raises(StorageError):
        MockStorageClient(tmp_path / "b").upload_bytes("../fuera.txt", b"x", "text/plain")
