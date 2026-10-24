# Especificación Técnica — Motor de Recomendaciones Helios v2.4

> Artefacto técnico ficticio · Nébula Labs · Documento de densidad media
> Clasificación: Confidencial · Owner: Equipo de Personalización · Fecha: 2026-08-30
> Extensión estimada: 10 páginas · Codificación UTF-8 · Sin datos reales

---

## 1. Resumen ejecutivo

Helios es el motor de recomendaciones de Nébula Labs para catálogos de entre 50.000 y 4 millones de ítems. La versión 2.4 reemplaza el ranking basado en reglas por un modelo de dos etapas: recuperación aproximada y reordenamiento con features de negocio.

El objetivo es aumentar la tasa de clic en un 8 % relativo sin degradar la latencia p99 por encima de 120 ms. El documento describe la arquitectura, los contratos de datos, la API pública y el plan de evaluación.

La adopción se mide por el porcentaje de peticiones que consumen al menos una recomendación en la primera pantalla. En la línea base de v2.3 ese indicador era 71,4 %; la meta para v2.4 es 78 %. El equipo de Personalización es responsable del modelo y el equipo de Plataforma de la latencia.

- Recuperación: ANN sobre embeddings de 256 dimensiones (HNSW, M=32).
- Reordenamiento: modelo gradient boosting con 42 features.
- Explicabilidad: motivos de recomendación devueltos por la API.

---

## 2. Objetivos y no objetivos

Los objetivos se priorizan por impacto en negocio y riesgo operativo. Cada objetivo tiene una métrica asociada y un umbral de aceptación medido en el experimento A/B.

No forma parte de esta versión la personalización en tiempo real por sesión anónima, ni la optimización de precios. Ambas quedan para Helios 3.0 y requieren revisión de privacidad.

Cada objetivo se revisa al cierre del trimestre con evidencia del panel de experimentos. Los objetivos no alcanzados no bloquean el despliegue, pero requieren un análisis escrito y una decisión explícita del comité de producto antes de continuar con la siguiente fase.

- O-1: CTR@10 ≥ +8 % relativo frente a v2.3.
- O-2: cobertura de catálogo ≥ 62 % en 7 días.
- O-3: latencia p99 ≤ 120 ms con 6.000 req/s.
- N-1: no se usan datos sensibles ni atributos protegidos.

---

## 3. Arquitectura de referencia

El flujo se divide en ingestión de eventos, construcción de features, recuperación de candidatos y reordenamiento. Los servicios se comunican por gRPC y comparten un contrato Protobuf versionado en el repositorio helios-contracts.

La comunicación entre candidate-service y ranker incluye el identificador de la versión del modelo y la marca de tiempo del índice. Esa información se propaga hasta la respuesta para facilitar la depuración de recomendaciones inconsistentes entre réplicas durante un despliegue.

- event-collector: valida y publica eventos en Kafka (tópico rec.events.v2).
- feature-store: materializa features en Redis 7.4 con TTL de 15 minutos.
- candidate-service: ANN en memoria, replica el índice cada 10 minutos.
- ranker: modelo GBDT servido con ONNX Runtime 1.19.

| Servicio | Réplicas | CPU / Memoria | Dependencia crítica |
|---|---|---|---|
| event-collector | 3 | 1 vCPU / 2 GiB | Kafka |
| feature-store | 4 | 2 vCPU / 8 GiB | Redis |
| candidate-service | 6 | 4 vCPU / 16 GiB | Índice ANN |
| ranker | 8 | 2 vCPU / 4 GiB | feature-store |

---

## 4. Flujo de ingestión de eventos

Los clientes envían eventos de impresión y clic al endpoint /v2/events. El colector aplica validación de esquema con Protobuf, descarta duplicados por event_id durante 24 horas y publica en Kafka con clave user_id para preservar el orden por usuario.

La latencia de ingestión objetivo es p95 ≤ 400 ms. Los eventos con más de 5 minutos de retraso se enrutan a una cola de cuarentena para inspección manual.

El colector aplica muestreo del 1 % para eventos de impresión cuando la carga supera el 80 % de su capacidad. El muestreo es determinista por hash de user_id, de modo que un mismo usuario conserva la misma decisión durante la ventana de muestreo y las métricas siguen siendo comparables.

- Particiones: 24; factor de replicación: 3.
- Retención: 72 horas; compactación deshabilitada.
- Esquema versionado con compatibilidad hacia atrás obligatoria.

---

## 5. Modelo de datos

El almacén principal es PostgreSQL 16.3 para metadatos de catálogo y auditoría de modelos. Las features en línea viven en Redis y se reconstruyen desde el lago de datos si se pierden.

Las migraciones se aplican con una herramienta interna que exige revisión de un segundo ingeniero y un plan de reversa. Las tablas de interacciones usan particiones mensuales y una política de archivado que mueve particiones con más de 18 meses a Object Storage.

| Tabla | Clave | Retención | Notas |
|---|---|---|---|
| items | item_id | permanente | Metadatos y estado editorial |
| interactions | event_id | 18 meses | Particionada por mes |
| model_runs | run_id | 36 meses | Métricas y artefactos |
| experiments | exp_id | permanente | Asignación y variantes |

---

## 6. API pública v2

La API expone recomendaciones por usuario o por contexto de ítem. Todas las llamadas requieren OAuth 2.0 con alcance rec:read y aceptan un máximo de 50 ítems por respuesta.

La paginación es por cursor opaco. Los errores siguen el formato problem+json con un código estable y un trace_id para soporte.

El contrato OpenAPI se genera a partir de anotaciones en el código y se publica en el portal interno en cada release. Los clientes reciben un aviso con 30 días de antelación ante cualquier cambio incompatible y disponen de un entorno de pruebas con datos sintéticos.

- GET /v2/recommendations?user_id=&limit=&cursor=
- GET /v2/similar?item_id=&limit=
- POST /v2/events (lote máximo de 500 eventos)
- GET /v2/health y GET /v2/ready para sondas.

---

## 7. Algoritmo de ranking

El reordenamiento combina señales de afinidad, popularidad, frescura y margen. Los pesos se calibran por vertical y se validan con un conjunto de evaluación congelado cada semana.

Se aplican reglas de diversidad para evitar que un mismo editor ocupe más del 30 % de la lista. Las listas se recalculan cada 15 minutos para usuarios activos.

El entrenamiento se ejecuta semanalmente sobre una ventana móvil de 90 días. Antes de publicar un modelo se comparan sus métricas offline con el modelo en producción y se rechaza si la ganancia en NDCG@10 es inferior a 0,5 puntos o si alguna vertical pierde más de un 1 %.

| Señal | Peso | Actualización | Fuente |
|---|---|---|---|
| Afinidad usuario–ítem | 0,38 | 15 min | Feature store |
| Popularidad 7 días | 0,24 | 1 h | Agregados Kafka |
| Frescura del ítem | 0,18 | 24 h | Catálogo |
| Margen estimado | 0,12 | 24 h | Finanzas |
| Diversidad | 0,08 | Por request | Reglas |

---

## 8. Evaluación y métricas

La evaluación offline usa NDCG@10 y recall@100 sobre una muestra estratificada por vertical. La evaluación online se realiza con un experimento A/B de cuatro semanas y asignación 50/50 por user_id.

Un experimento se detiene si la tasa de rebote aumenta más de 2 puntos porcentuales o si la latencia p99 supera el presupuesto durante tres días consecutivos.

Los paneles de evaluación muestran intervalos de confianza y el tamaño de muestra acumulado. La lectura de resultados se bloquea hasta alcanzar la potencia estadística planificada, salvo que se active una regla de parada por daño en las métricas de guarda.

- Métrica primaria: CTR@10.
- Métricas de guarda: rebote, latencia p99, cobertura.
- Prueba de significancia: secuencial con alpha 0,05.

---

## 9. Seguridad y privacidad

El motor no utiliza atributos protegidos ni datos de menores. Los identificadores de usuario se pseudonimizan con HMAC-SHA256 y una sal rotada cada 90 días.

El acceso a features sigue el principio de mínimo privilegio mediante roles de servicio. Toda lectura de datos personales queda auditada con retención de 12 meses.

Los proveedores de identidad envían únicamente identificadores seudonimizados; el motor no recibe correo, teléfono ni nombre. Los registros de auditoría se almacenan por separado y solo el equipo de Seguridad tiene permiso de lectura sobre ellos.

- Cifrado en tránsito TLS 1.3 y en reposo con claves gestionadas en Vault.
- Borrado por solicitud: propagación en ≤ 72 horas a features y almacén.
- Revisión de privacidad obligatoria para cualquier feature nueva.

---

## 10. Despliegue, riesgos y siguientes pasos

El despliegue es gradual: 5 %, 25 %, 50 % y 100 % del tráfico, con verificación automática de métricas de guarda entre etapas. El rollback revierte la versión del ranker y el índice de candidatos de forma atómica.

El principal riesgo es el sesgo de popularidad en catálogos nuevos. Se mitiga con un periodo de exploración del 10 % y con cuotas por editor.

El plan de comunicación incluye a soporte, éxito del cliente y marketing. Cada etapa tiene un responsable, una ventana horaria permitida y un criterio de aborto. El informe final se archiva junto con la decisión y las métricas crudas del experimento.

- Semana 1: sombra sin impacto en usuario.
- Semana 2: 5 % y revisión de métricas.
- Semanas 3–4: escalado gradual a 100 %.
- Cierre: informe de experimento y decisión de adopción.

---
