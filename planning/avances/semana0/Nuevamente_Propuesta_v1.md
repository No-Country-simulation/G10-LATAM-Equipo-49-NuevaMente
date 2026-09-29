NuevaMente – Sistema Inteligente

de Adaptación y Generación de Contenido Educativo

1.Planteamiento del problema

La documentación técnica suele estar diseñada para personas que ya
poseen cierto nivel de conocimiento. Convertir un mismo documento en
material educativo para diferentes audiencias requiere tiempo,
conocimiento técnico y trabajo editorial.

NuevaMente busca automatizar parte de este proceso mediante inteligencia
artificial.

El sistema utilizará documentación técnica como fuente de conocimiento y
generará diferentes tipos de contenido educativo según:

>  Perfil del destinatario.  Contexto o industria.  Formato
> pedagógico.

La generación deberá mantenerse vinculada a las fuentes originales para
facilitar la trazabilidad y reducir la generación de información no
sustentada.

2\. Visión del producto

NuevaMente será una aplicación capaz de recibir documentación técnica y
convertirla en diferentes productos educativos personalizados.

El mismo documento podrá utilizarse, por ejemplo, para generar:

> MISMO DOCUMENTO │
>
> ┌─────────────┼─────────────┐ ▼ ▼ ▼
>
> Principiante Developer Ejecutivo │ │ │
>
> Tutorial Quiz Resumen │ │ │
>
> └─────────────┼─────────────┘ ▼
>
> CONTENIDO EDUCATIVO +
>
> FUENTES / RAG +
>
> JSON +
>
> OCI STORAGE

La visión de segundas versiones despues del MVP, puede incorporar más
perfiles, formatos, agentes, modelos, integraciones y capacidades
educativas.

No forman parte del primer MVP.

3\. Product Goal

Construir una aplicación funcional que transforme documentación técnica
en contenido educativo personalizado, utilizando RAG y un LLM,
manteniendo trazabilidad hacia las fuentes originales y almacenando
documentos y resultados en OCI Object Storage.

El Product Goal funciona como el principal criterio para tomar
decisiones de alcance.

Cuando aparezca una nueva funcionalidad, Nos debemos preguntar:

¿Esta funcionalidad es necesaria para alcanzar el Product Goal del MVP?

Si la respuesta es no, puede permanecer en el Product Backlog para una
versión posterior.

4\. Usuario objetivo

Para el MVP se define un usuario principal:

Instructor, especialista técnico o diseñador instruccional que necesita
convertir documentación técnica en material educativo para diferentes
audiencias.

No se intentará resolver simultáneamente las necesidades de:

>  Alumnos.
>
>  Administradores.  Empresas.
>
>  Profesores.
>
>  Usuarios finales de un LMS.

Estos perfiles pueden formar parte de futuras versiones.

5\. Alcance del MVP

Formatos de entrada

El MVP soportará:

>  PDF.
>
>  Markdown.  TXT.

Perfiles

Inicialmente se trabajará con:

>  Principiante.
>
>  Developer Jr/Semi Sr.  Gestor/Ejecutivo.

Formatos pedagógicos

Se limitará inicialmente a:

>  Tutorial paso a paso.  Resumen ejecutivo.

 Quiz con justificaciones. Contexto

El contexto o industria se manejará como un parámetro libre, evitando
construir una matriz fija de industrias.

Procesamiento

El MVP deberá implementar:

Documento ↓

OCI Object Storage ↓

Extracción ↓

Chunking ↓

Embeddings ↓

Vector Store ↓

Retrieval / RAG ↓

Personalización ↓

LLM ↓

Evaluación

> ↓ JSON ↓

OCI Object Storage ↓

Visualización

6\. Fuera de alcance

Para proteger el alcance del MVP quedan inicialmente fuera:

>  Autenticación y gestión de usuarios.  Aplicación móvil.
>
>  Fine-tuning.
>
>  Múltiples proveedores LLM simultáneos.  LMS completo.
>
>  Analítica avanzada.
>
>  Dashboard administrativo.  Video.
>
>  Voz.
>
>  Chatbot independiente.
>
>  Editor educativo avanzado.
>
>  Sistema multiagente autónomo complejo.  Gran cantidad de formatos
> pedagógicos.  Gran cantidad de perfiles.

Estas funcionalidades pueden registrarse como oportunidades para
versiones posteriores.

7\. Criterios de éxito del MVP

El MVP debe permitir que una persona externa al equipo pueda realizar el
siguiente flujo sin intervención técnica:

Prueba 1 — Ingesta

Cargar un documento PDF, Markdown o TXT.

Resultado esperado: el documento queda almacenado en OCI y recibe un
document_id.

Prueba 2 — Recuperación

Realizar una consulta relacionada con el documento.

Resultado esperado: el sistema recupera fragmentos relevantes y genera
una respuesta fundamentada en ellos.

Prueba 3 — Personalización

Seleccionar:

>  Principiante.  Fintech.
>
>  Tutorial.

Resultado esperado: se genera un tutorial adaptado a ese perfil y
contexto.

Prueba 4 — Cambio de audiencia

Utilizar el mismo documento y seleccionar:

>  Ejecutivo.  Fintech.
>
>  Resumen ejecutivo.

Resultado esperado: se genera un resultado diferente, adaptado a la
nueva audiencia.

Prueba 5 — Trazabilidad

El resultado debe identificar las fuentes utilizadas.

Por ejemplo:

"sources": \[ {

> "chunk_id": "chunk-18", "page": 7

} \]

Prueba 6 — JSON

El usuario debe poder descargar el resultado como JSON.

Prueba 7 — Persistencia

El resultado generado debe quedar almacenado en OCI Object Storage.

8\. Marco de trabajo Scrum

Scrum se utilizará como marco para organizar el desarrollo incremental
del producto.

El objetivo será proporcionar una guía para dividir el trabajo en
semanas, además de definir de manera clara para todos los integrantes
del equipo los siguientes :

>  Objetivo de producto.
>
>  Product Backlog Lista de funciones del producto.  Priorización.
>
>  Sprints con objetivos concretos.  Incrementos funcionales.
>
>  Pruebas a realizar
>
>  Una Definition of Done compartida.

9\. Roles

Para un equipo de 5–6 personas se propone:

> Rol
>
> Scrum/Lider r
>
> Data/RAG Engineer
>
> AI/LLM Engineer

Responsabilidad

Facilitar Scrum, eliminar impedimentos y mejorar el proceso

Ingesta, chunking, embeddings y retrieval

> Prompts, generación y evaluación
>
> Cloud/Backend Engineer OCI, backend e integración
>
> Frontend/UX / QA Streamlit, experiencia, pruebas y validación

Los roles técnicos pueden combinarse según el tamaño real del equipo.

10\. Product Backlog

El Product Backlog representa el trabajo necesario para evolucionar el
producto.

Se organizará mediante épicas → historias de usuario → tareas técnicas.

11.Criterios de aceptación

Definir en equipo, los criterios de éxito del entregable: ¿Qué debe
cumplir esta historia específica? Ejemplo:

El usuario puede cargar PDF, TXT y Markdown y el documento queda
almacenado en OCI.

Definition of Done

Definir en equipo o conocer las condiciones necesarias para considerar
terminado un entregable:

¿Qué condiciones generales debe cumplir cualquier historia para
considerarse terminada?

Una historia está Done cuando:  Está implementada.

>  Cumple sus criterios de aceptación.  Funciona.
>
>  Fue probada.
>
>  Tiene manejo básico de errores.
>
>  Está integrada al flujo correspondiente.  No deja trabajo crítico
> pendiente.
>
>  Puede ser demostrada por el equipo.

12\. Priorización

Se utilizará una priorización sencilla:

> Prioridad Significado
>
> P0 Necesaria para demostrar el MVP
>
> P1 Importante, pero puede diferirse
>
> P2 Evolución posterior
>
> P3 Fuera del MVP inicial

La prioridad se establecería para usarse como guía para no desviar
esfuerzos en funcionalidades que no estén en el alcance del MVP.

Esto es importante para tener claro cuales funcionalidades deben
priorizarse para el MVP, y solo desarrollarse si se ha terminado el MVP
