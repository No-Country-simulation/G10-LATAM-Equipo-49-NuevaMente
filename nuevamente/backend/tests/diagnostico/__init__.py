"""Diagnóstico del defecto reportado (2026-10-24).

Síntoma reportado en el ambiente de AWS EC2:
    "Al generar contenido parece estar generando el mismo tipo, aunque se
     seleccione otro tipo de contenido. Cohere es el proveedor de LLM y de
     embeddings."

Estos tests NO son de aceptación: son una **simulación reproducible** del
camino que recorre una solicitud real en ese ambiente, más controles
(xfail(strict)) que describen el comportamiento esperado y que hoy fallan.

Convención (igual que `tests/audit/README_AUDITORIA.md`):

    XFAIL (strict)  -> defecto confirmado y todavía presente
    PASSED          -> control positivo / caracterización del estado actual

Cuando se implemente la corrección, los `xfail` pasarán a `XPASS(strict)`
(es decir, FAILED) y habrá que quitarles el marcador: en ese momento se
convierten en regresiones permanentes.

Todo corre sin red y sin credenciales: `tests/conftest.py` fuerza
`LLM_PROVIDER=mock`, `EMBEDDING_PROVIDER=mock` y `VECTORSTORE_PROVIDER=memory`.
"""
