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
import unicodedata
from collections.abc import Iterator

from src.generation.profiles import STOPWORDS

DIM = 256
_TOK = re.compile(r"[a-z0-9]+")


def _normalize(text: str) -> str:
    """Minúsculas sin acentos (NFKD + descarte de marcas diacríticas)."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def _indices(text: str) -> Iterator[int]:
    """Índices de dimensión para cada token significativo de `text`.

    *********************************************************************
    MEJORA AUD-010 — 2026-10-15
    Antes se contaban TODOS los tokens (incluidas stopwords como "de", "la",
    "y") sin normalizar acentos. Una consulta ajena al documento
    ("receta de paella…") compartía stopwords y puntuaba 0.31-0.62, por encima
    del umbral 0.25, de modo que NO_CONTEXT era inverificable de extremo a
    extremo. Ahora se descartan stopwords y se normalizan acentos, de modo que
    solo las palabras de contenido aportan similitud.

    El índice es `hash(token) % DIM`, estable entre ejecuciones y entre
    procesos. Las colisiones solo suman apariciones en la misma dimensión,
    lo cual es aceptable para un proveedor mock.
    *********************************************************************
    """
    for token in _TOK.findall(_normalize(text)):
        if token in STOPWORDS or len(token) < 2:
            continue
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
