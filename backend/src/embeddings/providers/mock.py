"""EmbeddingProvider en modo mock, determinista y sin red (DT-09 mock).

Misma idea que un hashing de tokens: cada token conocido mapea a un índice
fijo de un vector normalizado de dimensión fija. Mismo texto → mismo vector
(reproducibilidad para tests); textos con tokens en común tienen similaridad
coseno > 0 — suficiente para el vertical slice sin credenciales reales.
"""
import math
import re

DIM = 256
_VOCAB: dict[str, int] = {}
_TOK = re.compile(r"[a-záéíóúñü0-9]+")


def _indices(text: str) -> list[int]:
    for token in _TOK.findall(text.lower()):
        if token not in _VOCAB:
            _VOCAB[token] = len(_VOCAB)
            # reset a 0 cuando el vocabulario trivial llena la dimensión
            if len(_VOCAB) >= DIM:
                _VOCAB.clear()
        if token in _VOCAB and _VOCAB[token] < DIM:
            yield _VOCAB[token]


def _vector(text: str) -> list[float]:
    vec = [0.0] * DIM
    for i in _indices(text):
        vec[i] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class MockEmbeddingProvider:
    """Cumple `EmbeddingProvider` de forma determinista, sin red."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [_vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return _vector(text)