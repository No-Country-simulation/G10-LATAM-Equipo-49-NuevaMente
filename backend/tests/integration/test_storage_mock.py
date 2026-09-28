"""Storage en modo mock: subida, verificación y listado (COMP-09 offline).

QA para `MockStorageClient` + helpers `upload_original`/`upload_result_json`,
sin golpear la red (misma interfaz que el cliente OCI real).
"""
from src.storage.base import StorageClient
from src.storage.mock_client import MockStorageClient
from src.storage.upload import upload_original, upload_result_json


def _cliente() -> MockStorageClient:
    import tempfile

    return MockStorageClient(root=tempfile.mkdtemp())


def test_upload_bytes_y_verificacion():
    client = _cliente()
    res = client.upload_bytes("originales/d1/doc.txt", b"hola", "text/plain")
    assert client.object_exists(res.object_name)
    assert not client.object_exists("originales/d1/otro.txt")


def test_upload_original_nombra_por_documento():
    client = _cliente()
    res = upload_original("abc123", "nota.md", b"# titulo", client)
    # convención DT-07: {tipo}/{doc_id}/{timestamp}_{nombre}
    assert res.object_name.startswith("originales/abc123/")
    assert res.object_name.endswith("nota.md")
    assert len(res.object_name) > len("originales/abc123/") + 8  # timestamp presente


def test_upload_resultado_json():
    client = _cliente()
    res = upload_result_json("abc123", "job456", b"{}", client)
    assert res.object_name.startswith("resultados/abc123/")
    assert res.object_name.endswith("job456.json")


def test_list_objects_por_prefijo_y_paginacion():
    client = _cliente()
    upload_original("doc1", "a.md", b"a", client)
    upload_original("doc1", "b.md", b"b", client)
    upload_result_json("doc1", "j1", b"{}", client)

    listing = client.list_objects(prefix="resultados/")
    assert listing.count == 1
    assert listing.objects[0].name.startswith("resultados/doc1/")
    assert listing.objects[0].name.endswith("j1.json")

    lista_originales = client.list_objects(prefix="originales/")
    assert lista_originales.count == 2


def test_mock_client_cumple_protocol_storage():
    """Garantía estática: la clase puede anotarse como `StorageClient`."""
    client: StorageClient = MockStorageClient()
    assert client.get_namespace() == "mock-namespace"