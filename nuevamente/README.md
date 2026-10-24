# Suite de diagnóstico — generación y formatos

<!-- CAMBIO H-01/H-02/H-03/H-04/H-05/H-08 INICIO — 2026-10-24 -->
Pruebas de regresión para los hallazgos reportados el 2026-10-24.
Complementan (no reemplazan) a `tests/audit/`.

## Cómo ejecutar

```bash
cd nuevamente/backend
python -m pytest tests/diagnostico -q -rxXs
```

No requiere red ni credenciales: `tests/conftest.py` fuerza
`LLM_PROVIDER=mock`, `EMBEDDING_PROVIDER=mock` y `VECTORSTORE_PROVIDER=memory`.
Los documentos se leen de `nuevamente/docs/documentos_demo/`.

## Qué cubre cada archivo

### `test_formato_repro.py`

Simula un fallo del proveedor y verifica que no se convierta en un resultado
mock presentado como exitoso.

### `test_generation_contract.py`

Contrato de `GenerationOrchestrator.generate_content` y del prompt v1:

- devuelve `ContenidoAdaptado` no vacío
- invoca al proveedor con el prompt construido
- el prompt pide la estructura del formato
- JSON inválido ⇒ `LLMProviderError`
- el schema contiene campos específicos para los cinco formatos

### `test_pipeline_copy.py`

- `/health` responde y los 3 documentos demo se ingestan (PASSED).
- El modo mock explícito termina con HTTP 200, `status=PARTIAL` y
  `generation_mode=mock`.

## Relación con el ambiente EC2

Si en EC2 el síntoma es "contenido repetido" y **no** errores 500, la imagen
desplegada no coincide con esta copia. Para verificarlo:

```bash
docker compose exec backend python -c "import inspect, src.generation.orchestrator as m; print(inspect.getsource(m.GenerationOrchestrator.generate_content))"
docker compose exec backend printenv | grep -E "LLM_PROVIDER|EMBEDDING_PROVIDER"
```

Y para medirlo de punta a punta contra el ambiente real:

```bash
docker cp nuevamente/backend/scripts/simular_formatos.py nuevamente-backend:/tmp/
docker cp nuevamente/docs/documentos_demo/atlas-pay-5p.md nuevamente-backend:/tmp/
docker compose exec backend python /tmp/simular_formatos.py \
    --documento /tmp/atlas-pay-5p.md
```

El script devuelve `exit 2` si detecta formatos idénticos, contenido mock o
falta de estructura, de modo que puede usarse como *smoke test* post-deploy.
<!-- CAMBIO H-01/H-02/H-03/H-04/H-05/H-08 FIN — 2026-10-24 -->
