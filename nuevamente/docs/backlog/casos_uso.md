# Casos de uso

## CU-001 · Generar contenido educativo adaptado desde un documento nuevo

**Actor:** Usuario (instructor/especialista técnico)

**Objetivo:** Obtener contenido educativo personalizado a partir de un documento técnico propio

**Precondiciones**

- Ninguna (primer uso del documento)

**Entrada**

Archivo (PDF/MD/TXT), perfil, formato, nicho (opcional), nivel de detalle

**Flujo principal**

1. Ingesta del archivo y validación de tipo/tamaño (<= 10 MB)
2. Subida del original a OCI y generación de document_id
3. Extracción de texto y chunking
4. Generación de embeddings y persistencia en Vector Store
5. Retrieval del contexto relevante (top-k)
6. Generación del contenido adaptado con el LLM
7. Validación de fidelidad (score + claims no soportados)
8. Ensamblado del JSON y persistencia en OCI
9. Visualización del resultado en la interfaz web

**Flujos alternos**

- Archivo inválido, corrupto o que excede el tamaño: error controlado, no se sube
- PDF sin texto (escaneado): advertencia explícita, sin crash
- Sin contexto relevante: status NO_CONTEXT, no se genera libremente

**Salida**

contenido_adaptado + score de fidelidad + referencias a la fuente, visible en la interfaz

**Errores posibles**

- Archivo inválido o vacío
- Documento sin texto extraíble
- Fallo del proveedor LLM/embeddings
- Fallo de red hacia OCI

## CU-002 · Generar el mismo documento para una audiencia distinta

**Actor:** Usuario

**Objetivo:** Reutilizar un documento ya indexado para producir contenido con otro perfil/formato

**Precondiciones**

- El documento ya fue ingerido e indexado (CU-001 ejecutado antes)

**Entrada**

document_id existente, nuevo perfil/formato/nicho/detalle

**Flujo principal**

1. Retrieval reutilizando los embeddings existentes
2. Generación del contenido adaptado
3. Validación de fidelidad
4. Ensamblado del JSON y persistencia en OCI

**Salida**

Nuevo contenido_adaptado distinto al anterior para el mismo documento

**Errores posibles**

- document_id inexistente (DOCUMENT_NOT_FOUND)

## CU-003 · Recibir aviso de fidelidad baja

**Actor:** Usuario

**Objetivo:** Ser advertido cuando el contenido generado no está bien sustentado en la fuente

**Precondiciones**

- Contenido ya generado

**Entrada**

contenido_adaptado + chunks fuente

**Flujo principal**

1. Extraer claims del contenido generado
2. Contrastar cada claim contra los chunks fuente
3. Calcular fidelidad_score en [0,1]
4. Mostrar score bajo el umbral y lista de claims no sustentados antes de usar el contenido

**Flujos alternos**

- Fallo del LLM-juez: score=null + advertencia explícita, no bloquea la entrega

**Salida**

Score bajo el umbral configurado + lista de claims no sustentados

**Errores posibles**

- Fallo del LLM-juez (se informa, no se oculta)

