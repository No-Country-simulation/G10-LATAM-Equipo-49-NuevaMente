# Guía de los 6 documentos de prueba — para qué escenario sirve cada uno

**Carpeta:** `documentos_demo/`
**Contenido:** 3 artefactos técnicos ficticios (empresa inventada “Nébula Labs”), cada uno en **PDF** y
**Markdown**, con extensiones de **5, 10 y 13 páginas**.
**Datos:** 100 % inventados. No contienen información real de personas, clientes ni credenciales.

| Documento base | PDF | Markdown | Páginas (PDF) | Palabras (MD) | Chunks ingeridos | Densidad |
|---|---|---|---:|---:|---:|---|
| Manifiesto de arquitectura — Atlas Pay v3.2 | `atlas-pay-5p.pdf` | `atlas-pay-5p.md` | **5** | 604 | 6 | Baja (“poca información”) |
| Especificación técnica — Helios Rec v2.4 | `helios-rec-10p.pdf` | `helios-rec-10p.md` | **10** | 1 534 | 17 (PDF) / 14 (MD) | Media |
| Runbook SRE + arquitectura — Plataforma Orión | `orion-platform-13p.pdf` | `orion-platform-13p.md` | **13** | 2 002 | 23 (PDF) / 19 (MD) | Alta |

> Los PDF tienen **exactamente** 5, 10 y 13 páginas (verificado con `pypdf`) y numeración “Página X de N”
> en el pie. Los Markdown declaran su extensión estimada y usan separadores `---` por página.
> Cada artefacto existe en ambos formatos con el **mismo contenido**, lo que permite una prueba
> controlada de paridad PDF ↔ Markdown.

---

## 1. `atlas-pay-5p.pdf` — 5 páginas, PDF, densidad baja

**Tema:** manifiesto de arquitectura de un servicio de pagos (componentes, SLO, riesgos).

**Mejor para:**
- **Smoke test del flujo completo** en la UI con un documento pequeño (sube rápido, resultado en segundos).
- **Validación de extracción PDF**: comprobar que `page_count=5`, que el texto se extrae y que no hay
  *warnings* de páginas vacías.
- **Demo corta** de 2–3 minutos para stakeholders (portada + 5 secciones claras).
- **Caso de documento con poca información**: útil como control para verificar que el sistema **no
  inventa** contenido cuando el contexto es escaso (comportamiento esperado: `NO_CONTEXT` o `PARTIAL`
  según el umbral de retrieval).
- **Prueba de chunking mínimo**: 6 chunks, fácil de inspeccionar a mano.

**No recomendado para:** evaluar calidad de RAG con múltiples temas o estrés de rendimiento.

**Verificación esperada:**
```bash
curl -F "file=@documentos_prueba/atlas-pay-5p.pdf" http://127.0.0.1:8000/ingest
# → 201, page_count=5, chunk_count≈6
```

---

## 2. `atlas-pay-5p.md` — 5 páginas equivalentes, Markdown, densidad baja

**Mejor para:**
- **Pruebas rápidas de CI** y desarrollo local (sin parser PDF, respuesta inmediata).
- **Validación del extractor Markdown** y del limpiado de encabezados/listas.
- **Prueba de contrato mínimo**: `page_count=0` (por diseño en MD) y `char_count` estable.
- **Comparación de formatos**: mismo contenido que el PDF de 5 páginas para verificar que el pipeline
  produce el mismo `chunk_count` y resultados equivalentes.



---

## 3. `helios-rec-10p.pdf` — 10 páginas, PDF, densidad media

**Tema:** especificación de un motor de recomendaciones (arquitectura, API, modelo de datos, ranking,
evaluación, seguridad y despliegue).

**Mejor para:**
- **Prueba de RAG multi-sección**: 10 secciones con temas diferenciados (API, ranking, seguridad,
  evaluación) permiten formular consultas por tema y verificar que las fuentes cambian (AUD-001).
- **Validación de metadatos de página**: el PDF conserva páginas reales; sirve para comprobar que
  `sources[].page` apunta a la página correcta.
- **Chunking de tamaño medio** (17 chunks): verifica cortes, overlap y que ningún chunk quede vacío.
- **Prueba de múltiples perfiles y formatos** sobre el mismo `document_id` (reutilización de embeddings).
- **Demostración de comparación de perfiles**: Principiante vs. Líder Técnico vs. Gestor.

**Verificación esperada:**
```bash
curl -F "file=@documentos_prueba/helios-rec-10p.pdf" http://127.0.0.1:8000/ingest
# → 201, page_count=10, chunk_count≈17
```

---

## 4. `helios-rec-10p.md` — 10 páginas equivalentes, Markdown, densidad media

**Mejor para:**
- **Retrieval por tema y nicho** sin costo de extracción PDF.
- **Pruebas de formato de salida** (Tutorial, Flashcards, Quiz, TL;DR, Guion) sobre un documento con
  suficiente sustancia.
- **Regresión de secciones**: el Markdown conserva encabezados `##`, útiles para validar `section` en los
  chunks.
- **Prueba de reingesta**: subir el mismo archivo dos veces y comprobar `document_id` nuevo + índice sin
  duplicados lógicos.
- **Comparación PDF vs MD**: mismo contenido, distinto `page_count` (10 vs 0) y distinto `char_count`
  por la metadata del PDF.

---

## 5. `orion-platform-13p.pdf` — 13 páginas, PDF, densidad alta

**Tema:** runbook de operaciones y arquitectura de plataforma (topología, SLO, alertas, diagnóstico,
despliegue, capacidad, DR, seguridad, postmortems).

**Mejor para:**
- **Prueba de estrés de chunking**: 23 chunks, varias tablas y secciones; ideal para validar offsets,
  overlap y ausencia de chunks vacíos en documentos largos.
- **Rendimiento de ingesta**: medir tiempo de extracción + embeddings + indexación con el documento más
  grande del set.
- **Persistencia y reindexado**: ingerir, reiniciar el proceso y verificar `_ensure_indexed` / conteo en
  Chroma.
- **Prueba de `MAX_DOCUMENT_CHARS`** de forma cualitativa (13 páginas ≈ 11,6 k caracteres; aún lejos del
  límite de 2 M, por lo que para el límite exacto se requiere un documento sintético).
- **Escenario ejecutivo**: resumen TL;DR de un runbook extenso, con muchas fuentes candidatas.
- **Validación de `sources`**: comprobar que el top-k no siempre cae en las primeras páginas.

**Verificación esperada:**
```bash
curl -F "file=@documentos_prueba/orion-platform-13p.pdf" http://127.0.0.1:8000/ingest
# → 201, page_count=13, chunk_count≈23
```

---

## 6. `orion-platform-13p.md` — 13 páginas equivalentes, Markdown, densidad alta

**Mejor para:**
- **Chunking máximo del set** por Markdown (19 chunks) y prueba de encabezados/secciones.
- **Validación de claims**: documento con muchas afirmaciones técnicas, útil para revisar
  `claims_no_soportados` y el score heurístico.
- **Prueba de retrieval con consultas específicas** (“lag de Kafka”, “rollback”, “RTO/RPO”).
- **Escenario de documento extenso en CI** sin depender del parser PDF.

---

## 7. Matriz rápida de elección

| Necesito probar… | Documento recomendado |
|---|---|
| Humo / demo de 2 minutos en la UI | `atlas-pay-5p.pdf` |
| Iteración rápida en CI | `atlas-pay-5p.md` |
| Documento con poca información / posible `NO_CONTEXT` | `atlas-pay-5p.pdf` o `.md` |
| Extracción de páginas PDF y `sources[].page` | `helios-rec-10p.pdf` u `orion-platform-13p.pdf` |
| RAG por temas y comparación de perfiles | `helios-rec-10p.pdf` / `.md` |
| Variedad de formatos de salida (5 formatos) | `helios-rec-10p.md` |
| Estrés de chunking y rendimiento | `orion-platform-13p.pdf` |
| Persistencia / reindexado / reinicio | `orion-platform-13p.pdf` |
| Claims y fidelidad con mucho texto | `orion-platform-13p.md` |
| Paridad PDF ↔ Markdown | pares del mismo tamaño (5, 10 o 13) |

---

## 8. Cómo usarlos

### Opción A — API directa

```bash
# 1. Ingesta
curl -F "file=@documentos_prueba/helios-rec-10p.pdf" http://127.0.0.1:8000/ingest

# 2. Adaptación 
curl -X POST http://127.0.0.1:8000/adapt \
  -H "Content-Type: application/json" \
  -d '{"document_id":"doc_...","perfil":"Desarrollador Junior / Semi Senior","formato":"Resumen Ejecutivo (TL;DR)","nicho":"General"}'

# 3. Consulta
curl http://127.0.0.1:8000/adapt/job_...
```

### Opción B — Interfaz Streamlit

1. `run_api.bat` (o `./run_api.sh`).
2. `run_ui.bat` (o `./run_ui.sh`).
3. Subir el archivo desde la pantalla de carga, elegir perfil/formato/nicho y consultar el resultado.

### Estado actual observado (2026-10-23)

| Etapa | Resultado |
|---|---|
| `/ingest` con los 6 documentos | **OK** (201; páginas y chunks correctos) |
| `/adapt` con los 6 documentos 


---

## 9. Nota sobre los datos

- Empresa, productos, personas, métricas, endpoints y buckets son **inventados**.
- No hay correos, teléfonos, API keys, tokens ni nombres de personas reales.
- Los textos están en español (UTF-8) e incluyen acentos, tablas y guiones largos para probar la
  codificación de extremo a extremo.
- Se pueden versionar y reutilizar libremente dentro del proyecto.
