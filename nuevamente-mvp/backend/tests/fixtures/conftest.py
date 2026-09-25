import os
import pathlib
import pytest

os.environ["LLM_PROVIDER"] = "mock"
os.environ["EMBEDDING_PROVIDER"] = "mock"
os.environ["ENVIRONMENT"] = "test"
os.environ["CHROMA_PERSIST_DIR"] = "./data/chroma_test"
os.environ["DATABASE_URL"] = "sqlite:///./data/sqlite/test.db"


@pytest.fixture(autouse=True)
def clean_test_dirs():
    yield
    for path in ["./data/chroma_test", "./data/sqlite/test.db", "./data/mock_oci"]:
        p = pathlib.Path(path)
        if p.is_file():
            p.unlink(missing_ok=True)


@pytest.fixture
def sample_text() -> str:
    return (
        "NuevaMente es una aplicación que transforma documentación técnica "
        "en contenido educativo adaptado. " * 40
    )


@pytest.fixture
def sample_pages() -> list[dict]:
    return [
        {"page": 1, "text": "Introducción a NuevaMente. " * 20},
        {"page": 2, "text": "Arquitectura del sistema. " * 20},
    ]
