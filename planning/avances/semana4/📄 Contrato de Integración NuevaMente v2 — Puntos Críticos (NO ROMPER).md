

# 🔒 Contrato de Integración — NuevaMente v2

## Puntos críticos que NO deben modificarse sin coordinación previa

**Autor:** Rodrigo Reyes (Orquestación n8n)  
**Fecha:** 6 oct 2026  
**Versión:** 2.0  
**Contexto:** Este documento define el contrato entre el backend FastAPI y el orquestador n8n. Cualquier cambio en estos puntos rompe el flujo de producción.


## 📌 1. ENDPOINTS (API REST)

| Endpoint | Método | Propósito | Response Code |
| - | - | - | - |
| `/health` | `GET` | Smoke test del backend | `200` |
| `/ingest` | `POST` | Subir documento (PDF/MD/TXT) | `201` |
| `/adapt` | `POST` | Solicitar adaptación asíncrona | `202` |
| `/adapt/\{job\_id\}` | `GET` | Consultar estado del job | `200` / `202` / `404` |


⚠️ **NO CAMBIAR:** Nombres de endpoints ni métodos HTTP.


## 📥 2. REQUESTS (Entrada)

### 2.1 POST `/ingest`

Content-Type: multipart/form-data Campo obligatorio: file (binario)

### 2.2 POST `/adapt`

***Content-Type: multipart/form-data Campo obligatorio: file (binario)**

### 2.2 POST `/adapt`

```
\{  
  "document\_id": "string",  
  "perfil": "Principiante | Junior | Arquitecto | Ejecutivo",  
  "formato": "Tutorial | Flashcards | Quiz | TLDR | Guion",  
  "nicho": "Fintech | Salud | E-commerce | General"  
\}
```

⚠️ ***NO CAMBIAR: Nombres de campos (`document\_id`, `perfil`, `formato`, `nicho`) ni valores permitidos de los enums.**

📤 ***3. RESPONSES (Salida)**


### ***3.1 POST `/ingest` → `201 Created`**

***`\{`**

***`  "document\_id": "string",`**

***`  "file\_type": "pdf | md | txt",`**

***`  "status": "INGESTED",`**

***`  "filename": "string",`**

***`  "size\_bytes": "int",`**

***`  "page\_count": "int",`**

***`  "char\_count": "int",`**

***`  "chunk\_count": "int",`**

***`  "storage\_object\_name": "string",`**

***`  "warnings": \["string"\]`**

***`\}`**

### ***3.2 POST `/adapt` → `202 Accepted`**

\{

  "job\_id": "string",

  "status": "PROCESSING"

\}

### ***3.3 GET `/adapt/\{job\_id\}` → `202` (aún procesando)**

\{

  "job\_id": "string",

  "status": "QUEUED | PROCESSING"

\}

### ***3.4 GET `/adapt/\{job\_id\}` → `200` (completado)**

***\{**

***  "status": "exito",**

***  "metadatos": \{**

***    "doc\_id": "string",**

***    "perfil": "string",**

***    "formato": "string",**

***    "nicho": "string",**

***    "tiempo\_estimado\_estudio\_minutos": "int",**

***    "conceptos\_clave": \["string"\],**

***    "sources": \[\{"chunk\_id": "string", "page": "int"\}\]**

***  \},**

***  "contenido\_adaptado": \{**

***    "titulo": "string",**

***    "introduccion\_contextualizada": "string",**

***    "items": \[\]**

***  \},**

***  "evaluacion\_calidad": \{**

***    "fidelidad\_score": "float (0.0 - 1.0) | null",**

***    "claridad\_pedagogica": "Alta | Media | Baja",**

***    "observaciones": \["string"\]**

***  \},**

***  "almacenamiento\_oci": \{**

***    "bucket": "string",**

***    "object\_name\_original": "string",**

***    "object\_name\_json": "string",**

***    "uploaded\_at": "ISO 8601"**

***  \}**

***\}**


### ***3.5 Error responses (`400` / `404` / `500`)**

\{

  "error": \{

    "code": "string",

    "message": "string"

  \}

\}

⚠️ ***NO CAMBIAR:** ***Estructura de respuestas ni nombres de campos. Agregar campos nuevos es aceptable (retrocompatible), pero eliminar o renombrar existentes rompe el contrato.**

## **🎯 *4. VALORES CRÍTICOS PARA N8N (NO TOCAR)**

| Campo | Valor | Por qué es crítico |
| :-: | :-: | :-: |
| `fidelidad\_score` umbral | `≥ 0.9` | Nodo IF de n8n evalúa esto para controlar alucinaciones |
| `fidelidad\_score` en modo mock | `null` aceptado | Temporal hasta que RAG real esté implementado |
| Job status (polling loop) | `QUEUED`, `PROCESSING` | El loop de n8n espera estos valores para seguir consultando |
| Job status (completado) | Cualquier otro valor | Sale del loop y continúa al IF de fidelidad |
| Error code fidelidad | `FIDELIDAD\_BAJA` | Código específico que n8n devuelve al usuario |
| File types | `pdf`, `md`, `txt` | Validación de ingesta |
| Perfiles | `Principiante`, `Junior`, `Arquitecto`, `Ejecutivo` | Enums del contrato |
| Formatos | `Tutorial`, `Flashcards`, `Quiz`, `TLDR`, `Guion` | Enums del contrato |
| Nichos | `Fintech`, `Salud`, `E-commerce`, `General` | Enums del contrato |



## **🏗️ *5. FLUJO N8N V2 (Arquitectura Asíncrona)**


\[Webhook POST\] 

   ↓

\[HTTP Request: POST /ingest\] → devuelve document\_id

   ↓

\[HTTP Request: POST /adapt\] → devuelve job\_id

   ↓

\[Loop: Wait 3s + GET /adapt/\{job\_id\}\] → polling hasta status != PROCESSING/QUEUED

   ↓

\[IF: fidelidad\_score === null OR \>= 0.9\]

   ├─ true  → \[Respond 200: Paquete educativo completo\]

└─ false → \[Respond 400: Error FIDELIDAD\_BAJA\]


## ***6. REGLAS DE ORO DEL CONTRATO**


| ~~***\#** | ~~***Regla** | ~~***Por qué** |
| - | :-: | :-: |
| ~~***1** | ~~***No romper lo existente** | ~~***Si n8n o la UI ya usan un campo, no lo quites ni cambies su tipo** |
| ~~***2** | ~~***Agregar es mejor que cambiar** | ~~***Puedes agregar campos nuevos, pero no modificar los existentes sin aviso** |
| ~~***3** | ~~***Documentar cada cambio** | ~~***Si agregas un campo, actualiza este documento y el README** |
| ~~***4** | ~~***Validar siempre con Pydantic** | ~~***Rechaza lo inválido temprano, no tarde** |
| ~~***5** | ~~***Mantener retrocompatibilidad** | ~~***Los consumidores (n8n, UI) no deben romperse con cambios menores** |


  

