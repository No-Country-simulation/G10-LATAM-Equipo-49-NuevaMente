"""`EmbeddingProvider` en modo mock — determinista y sin red.

Permite desarrollar y probar el pipeline completo (ingesta → retrieval →
contexto) sin credenciales. Vectors por *hashing* de tokens: NO son
embeddings semánticos. Sirven para ejercitar la mecánica del RAG, no para
medir calidad de recuperación.

Determinismo (DT-05): el índice de cada token se deriva de un hash estable
del propio token, no del orden de aparición. Así el vector de un texto no
depende de qué otros textos se procesaron antes en el mismo proceso.
"""
import hashlib
import math
import re
from collections.abc import Iterator

DIM = 256
_TOK = re.compile(r"[a-záéíóúñü0-9]+")


def _indices(text: str) -> Iterator[int]:
    """Índices de dimensión para cada token de `text`.

    El índice es `hash(token) % DIM`, estable entre ejecuciones y entre
    procesos. Las colisiones solo suman apariciones en la misma dimensión,
    lo cual es aceptable para un proveedor mock.
    """
    for token in _TOK.findall(text.lower()):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
        yield int.from_bytes(digest, "big") % DIM


def _vector(text: str) -> list[float]:
    """Vector unitario de `text`: conteo de tokens normalizado."""
    vec = [0.0] * DIM
    for i in _indices(text):
        vec[i] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class MockEmbeddingProvider:
    """Cumple el contrato `EmbeddingProvider` sin llamar a ningún servicio externo."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [_vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return _vector(text)
