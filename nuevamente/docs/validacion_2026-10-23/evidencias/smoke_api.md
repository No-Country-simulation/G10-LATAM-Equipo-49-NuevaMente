# Evidencia HTTP — flujo completo

| Paso | HTTP | Respuesta (resumen) |
|---|---:|---|
| GET /health | 200 | `{"status": "ok"}` |
| POST /ingest (orion-platform-13p.pdf) | 201 | `{"document_id": "doc_035e5730b592", "file_type": "pdf", "status": "INGESTED", "filename": "orion-platform-13p.pdf", "size_bytes": 23670, "page_count": 13, "char_count": 11649, "chunk_count": 23, "storage_object_name": "o…` |
| POST /adapt (válido) | 202 | `{"job_id": "job_e0dad2b49074", "status": "PROCESSING"}` |
| GET /adapt/{job_id} (resultado) | 500 | `{"error": {"code": "INTERNAL_ERROR", "message": "Error interno durante la adaptación."}}` |
| GET /adapt/job_inexistente | 404 | `{"error": {"code": "JOB_NOT_FOUND", "message": "No existe un job con ese job_id"}}` |
| POST /adapt (documento inexistente) | 404 | `{"error": {"code": "DOCUMENT_NOT_FOUND", "message": "No existe un documento indexado con ese document_id"}}` |
| POST /adapt (perfil inválido) | 422 | `{"error": {"code": "INVALID_REQUEST", "message": "Solicitud inválida — body.perfil: Input should be 'Principiante / Transición de Carrera', 'Desarrollador Junior / Semi Senior', 'Líder Técnico / Arquitecto' or 'Gestor / …` |