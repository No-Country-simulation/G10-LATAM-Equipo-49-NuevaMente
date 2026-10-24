# Runbook de Operaciones y Arquitectura — Plataforma Orión

> Artefacto técnico ficticio · Nébula Labs · Documento de alta densidad
> Clasificación: Restringido · Owner: SRE Core · Fecha: 2026-10-02 · Revisión 7
> Extensión estimada: 13 páginas · Codificación UTF-8 · Sin datos reales

---

## 1. Cómo usar este runbook

Este runbook es la referencia operativa de la plataforma Orión, que aloja los servicios compartidos de Nébula Labs: identidad, mensajería, almacenamiento de objetos, colas de trabajo y observabilidad. Está escrito para ser usado durante un incidente, no para ser leído de principio a fin.

Cada sección de diagnóstico sigue el patrón: síntoma, verificación, mitigación y escalamiento. Los comandos asumen acceso al clúster vega-prod con el rol oncall-sre y kubectl configurado contra el contexto correcto.

El runbook se versiona en el mismo repositorio que los manifiestos de infraestructura. Cualquier cambio en un procedimiento debe incluir la actualización de este documento en el mismo pull request; de lo contrario, la revisión automática de documentación falla y el cambio no se aprueba.

- Severidad 1: pérdida de datos o indisponibilidad total. Escalar de inmediato.
- Severidad 2: degradación sostenida con impacto medible en clientes.
- Severidad 3: riesgo latente sin impacto actual.

---

## 2. Topología de la plataforma

Orión se despliega en tres clústeres: vega-prod (carga principal), vega-dr (recuperación) y vega-staging. La región primaria es mx-queretaro-1 y la secundaria mx-monterrey-1. La replicación de datos es asíncrona con un retraso objetivo menor a 60 segundos.

La plataforma expone un plano de control con Argo CD 2.13 y un plano de datos compuesto por Kong 3.8, Kafka 3.7, PostgreSQL 16.3, Redis 7.4 y OCI Object Storage.

Cada clúster tiene un pool de nodos dedicado para cargas con requisitos de latencia y otro para tareas por lotes. Los nodos de carga crítica usan discos locales efímeros para caché y no alojan estado persistente, de modo que su reemplazo no requiere migración de datos.

- Ingress: Kong con 3 réplicas y límite de 12.000 req/s por instancia.
- Mensajería: 4 brokers Kafka, 36 particiones por tópico crítico.
- Almacenamiento: bucket orion-prod-assets con versionado habilitado.

---

## 3. Dependencias y contratos entre servicios

Los contratos se publican como esquemas Protobuf y OpenAPI versionados. Un cambio incompatible requiere una nueva versión mayor y un periodo de convivencia de al menos dos releases.

Las dependencias críticas tienen timeouts, reintentos con jitter y circuit breaker. Nunca se reintenta una operación no idempotente sin clave de idempotencia.

Los contratos se validan en integración continua con pruebas de compatibilidad hacia atrás. Un consumidor que no puede actualizarse en el plazo acordado debe registrar una excepción con fecha de caducidad y un plan de migración aprobado por arquitectura.

| Consumidor | Proveedor | Timeout | Reintentos | Modo de fallo |
|---|---|---|---|---|
| identity-api | postgres-identity | 800 ms | 2 | Rechazo controlado |
| billing-api | kafka-core | 2 s | 3 | Cola local |
| search-api | redis-cache | 120 ms | 1 | Degradación |
| media-api | object-storage | 3 s | 2 | Error 503 |

---

## 4. SLOs y presupuesto de error

Los SLO se calculan con datos de OpenTelemetry y se consolidan en el panel «Orión — Confianza del servicio». El presupuesto de error se revisa en la reunión semanal de fiabilidad y su agotamiento implica congelar despliegues no urgentes.

Los SLO se revisan mensualmente con los owners de cada servicio. Si un SLO es demasiado laxo y no genera acciones, se propone endurecerlo; si es inalcanzable por diseño, se documenta la excepción y se ajusta el presupuesto con evidencia de capacidad.

- Disponibilidad del plano de datos: 99,95 % mensual.
- Latencia de identity-api: p95 ≤ 250 ms, p99 ≤ 700 ms.
- Retraso de replicación a DR: ≤ 60 s en el percentil 95.

| Servicio | SLI | SLO | Presupuesto mensual |
|---|---|---|---|
| identity-api | Disponibilidad | 99,95 % | 21,6 min |
| kafka-core | Mensajes entregados | 99,99 % | 4,3 min |
| object-storage | Lecturas exitosas | 99,9 % | 43,2 min |
| search-api | p95 | ≤ 300 ms | — |

---

## 5. Catálogo de alertas críticas

Cada alerta enlaza a una sección de este runbook y a un panel. Una alerta sin enlace a runbook se considera deuda operativa y debe corregirse en el siguiente sprint.

Las alertas se prueban cada trimestre con inyección de fallos controlada. Una alerta que no se dispara durante la prueba se marca como no confiable y se corrige antes del siguiente ciclo. Las alertas duplicadas se consolidan para reducir la fatiga del equipo de guardia.

| Alerta | Umbral | Severidad | Sección |
|---|---|---|---|
| IdentityErrorRateHigh | > 2 % durante 5 min | S1 | §7 |
| KafkaConsumerLagHigh | > 120.000 mensajes | S2 | §8 |
| ObjectStorage5xx | > 0,5 % durante 10 min | S2 | §7 |
| PostgresReplicaLag | > 45 s durante 5 min | S2 | §10 |
| DeployStuck | > 15 min sin progreso | S3 | §9 |

---

## 6. Diagnóstico: latencia p95 elevada

El síntoma habitual es un aumento sostenido de p95 sin caída de disponibilidad. Primero se descarta saturación de CPU o memoria en el servicio afectado; después se revisan las dependencias y, por último, el patrón de tráfico.

Si la latencia coincide con un despliegue reciente, se ejecuta rollback según §9. Si coincide con un pico de tráfico, se valida el HPA y se aplica escalado manual temporal.

Antes de escalar, se confirma que el problema no sea una consulta lenta o un bloqueo. Si el servicio depende de una base de datos, se revisan los planes de ejecución y las estadísticas; añadir réplicas sin corregir la consulta solo distribuye el problema.

- kubectl top pods -n orion-prod
- kubectl describe hpa identity-api -n orion-prod
- Consultar el panel de dependencias y el mapa de trazas.
- Comparar con la ventana de despliegues de las últimas 2 horas.

---

## 7. Diagnóstico: errores 5xx

Un incremento de 5xx se clasifica por origen: aplicación, base de datos, red o proveedor externo. La primera acción es identificar el servicio y la ruta con mayor tasa de error usando la agregación por atributo http.route.

Si el error es de conexión a PostgreSQL, se revisa el pool y las conexiones activas. Si es un timeout de Object Storage, se valida el estado del proveedor y se activa el modo de lectura desde caché.

El análisis de 5xx prioriza el impacto en clientes. Si el error afecta solo a una ruta de baja criticidad, la mitigación puede esperar a la ventana de cambios; si afecta autenticación o pagos, se trata como severidad 1 aunque la tasa sea pequeña.

- Verificar logs estructurados por trace_id.
- Revisar saturación del pool: pg_stat_activity y pgbouncer.
- Confirmar que el circuit breaker no está abierto de forma permanente.
- Escalar a Cloud/OCI si el proveedor reporta incidente.

---

## 8. Diagnóstico: saturación de Kafka

El indicador principal es el retraso del consumidor (consumer lag). Un lag creciente con throughput estable suele indicar un consumidor lento o bloqueado; un lag con throughput creciente indica un pico de producción.

Se comprueba el balanceo de particiones y se escala el grupo consumidor. Si una partición concentra el lag, se revisa la clave de particionado y se planifica una redistribución.

El lag se compara siempre con la línea base de la misma hora del día. Un valor absoluto alto puede ser normal en el pico de facturación; lo relevante es la tendencia y el tiempo estimado hasta vaciar la cola con el throughput actual.

- kafka-consumer-groups --describe --group orion-billing
- Revisar errores de deserialización en el consumidor.
- Escalar réplicas manteniendo el límite de particiones.
- Si el lag supera 4 horas, activar el plan de recuperación de §11.

---

## 9. Despliegue y rollback

Los despliegues son progresivos mediante Argo Rollouts: 10 %, 50 % y 100 %, con análisis automático de métricas. Un análisis fallido detiene el rollout y deja la versión anterior sirviendo tráfico.

El rollback manual se ejecuta con argocd app rollback y requiere confirmación de dos personas para servicios de severidad 1. Nunca se elimina una migración de base de datos durante el rollback.

Todo despliegue requiere un plan de reversa escrito, incluso si el cambio parece trivial. Los cambios de configuración usan el mismo proceso que el código y quedan registrados con el hash del commit y el identificador de la persona que aprobó.

- Verificar diff: argocd app diff orion-identity.
- Promover solo con aprobación del owner del servicio.
- Registrar el cambio en el canal #orion-releases.
- Actualizar el runbook si el procedimiento cambió.

---

## 10. Capacidad y escalado

La capacidad se planifica con una proyección trimestral basada en el crecimiento de tráfico y en el costo por transacción. El objetivo es mantener una holgura del 30 % en hora pico y del 50 % durante eventos especiales.

El escalado horizontal es automático para servicios sin estado; las bases de datos escalan verticalmente con ventana de mantenimiento y réplica previa.

La proyección de capacidad incorpora el costo unitario de cada servicio y el efecto de los contratos anuales. Un aumento de capacidad sin revisión de costo requiere justificación del owner y aprobación de Finanzas cuando supera el 15 % del presupuesto mensual.

- Revisión mensual de derechos de CPU y memoria.
- Prueba de carga trimestral con el 150 % del pico conocido.
- Alertas de capacidad al 75 % de uso sostenido.

---

## 11. Recuperación ante desastres

El plan de continuidad contempla RTO de 60 minutos y RPO de 15 minutos para los servicios de severidad 1. La conmutación a vega-dr es manual y requiere aprobación del incident commander y del owner de datos.

Cada trimestre se ejecuta un simulacro de conmutación con un servicio piloto. El informe del simulacro se adjunta a la revisión de continuidad.

El simulacro de recuperación mide tres tiempos: detección, decisión y conmutación efectiva. Los resultados se comparan con el simulacro anterior y se publican en el panel de continuidad. Una desviación superior al 20 % abre una acción correctiva obligatoria.

- Paso 1: declarar incidente y abrir sala de crisis.
- Paso 2: congelar escrituras en la región primaria.
- Paso 3: promover la réplica y actualizar DNS.
- Paso 4: validar integridad y reanudar tráfico.
- Paso 5: registrar tiempos reales frente a RTO/RPO.

---

## 12. Seguridad operativa y accesos

El acceso a producción es just-in-time, con aprobación y duración máxima de 4 horas. Los roles se asignan por grupo y se revisan trimestralmente. Las credenciales de larga vida están prohibidas.

Toda acción privilegiada queda auditada. Los secretos se rotan cada 90 días o de forma inmediata ante sospecha de exposición.

Los accesos de emergencia se revisan al cierre de cada incidente. Si una persona solicitó acceso sin justificación suficiente, se revoca de inmediato y se notifica a Seguridad. Los permisos permanentes se consideran una excepción y requieren compensación con controles adicionales.

- MFA obligatorio para consola y CLI.
- Registro de sesiones privilegiadas con retención de 12 meses.
- Revisión de accesos antes de cada auditoría externa.

---

## 13. Postmortems y mejora continua

Todo incidente de severidad 1 o 2 genera un postmortem sin culpables en un plazo de cinco días hábiles. El documento incluye línea de tiempo, impacto, causa raíz y acciones con responsable y fecha.

Las acciones se siguen en el tablero de fiabilidad. Un postmortem sin acciones verificables se considera incompleto y se devuelve al equipo.

Las lecciones se convierten en pruebas automatizadas cuando es posible. Un incidente cuya causa puede reproducirse en un test debe dejar una prueba de regresión antes de cerrar el postmortem; de lo contrario, la acción se considera incompleta.

- Plantilla: contexto, impacto, detección, respuesta, causa, acciones.
- Revisión en la reunión semanal de fiabilidad.
- Métrica de proceso: ≥ 80 % de acciones cerradas en 30 días.

---
