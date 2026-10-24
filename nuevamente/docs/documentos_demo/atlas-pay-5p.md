# Manifiesto de Arquitectura — Atlas Pay v3.2

> Artefacto técnico ficticio · Nébula Labs · Documento de baja densidad
> Clasificación: Interno · Owner: Arquitectura de Pagos · Fecha: 2026-09-18
> Extensión estimada: 5 páginas · Codificación UTF-8 · Sin datos reales

---

## 1. Propósito y estado del documento

Este manifiesto describe, a alto nivel, la arquitectura del servicio Atlas Pay v3.2, responsable de la autorización de pagos con tarjeta en Nébula Labs. El documento es deliberadamente breve: su objetivo es alinear al equipo y servir de punto de entrada, no sustituir las especificaciones detalladas de cada componente.

Atlas Pay procesa pagos en modalidad de autorización y captura diferida. La versión 3.2 introduce confirmación idempotente, firmas HMAC en webhooks y un presupuesto de error explícito por comercio. El estado del artefacto es «aprobado para implementación».

- Alcance: autorización, captura, reembolso y conciliación diaria.
- Fuera de alcance: originación de crédito, antifraude avanzado y facturación.
- Audiencia: arquitectura, desarrollo backend, SRE y equipos de integración.

---

## 2. Contexto y restricciones

El servicio se ejecuta sobre Oracle Kubernetes Engine (OKE) en la región mx-queretaro-1, con dos zonas de disponibilidad. La base transaccional es PostgreSQL 16.3 con réplica de lectura, y el bus de eventos es Kafka 3.7. Los secretos se gestionan en OCI Vault.

La latencia objetivo es p95 ≤ 180 ms para autorizaciones y p99 ≤ 450 ms. El sistema debe soportar 1.200 transacciones por segundo en hora pico y degradar de forma controlada: si el proveedor adquirente no responde, se responde con un código de reintento seguro.

- Idempotencia obligatoria mediante cabecera Idempotency-Key.
- Trazabilidad distribuida con OpenTelemetry y propagación W3C traceparent.
- Ningún dato de tarjeta completo se persiste: solo token y últimos cuatro dígitos.

---

## 3. Componentes principales

La arquitectura se organiza en cuatro componentes desplegables de forma independiente. La comunicación externa es REST/JSON; la interna usa gRPC con timeouts explícitos.

| Componente | Responsabilidad | Tecnología | Escalado |
|---|---|---|---|
| api-gateway | Autenticación, cuotas y enrutamiento | Envoy 1.31 | HPA 3–12 |
| payments-core | Máquina de estados del pago | Go 1.23 | HPA 4–20 |
| ledger-writer | Asientos contables inmutables | Go 1.23 | 2–8 |
| webhook-dispatcher | Entrega firmada con reintentos | Go 1.23 | 2–6 |

---

## 4. Objetivos de nivel de servicio

Los SLO se miden en ventanas móviles de 28 días y se publican en el panel «Atlas Pay — Salud del servicio». El incumplimiento sostenido durante dos ventanas consecutivas abre una revisión de arquitectura.

| Indicador | Objetivo | Ventana | Acción al agotar presupuesto |
|---|---|---|---|
| Disponibilidad de autorización | 99,95 % | 28 días | Congelar cambios no críticos |
| Latencia p95 | ≤ 180 ms | 28 días | Revisar índices y pools |
| Tasa de error 5xx | < 0,10 % | 28 días | Rollback del último release |
| Entrega de webhooks | ≥ 99,5 % en 5 min | 28 días | Aumentar workers |

---

## 5. Riesgos y decisiones abiertas

El riesgo principal es la dependencia del adquirente externo, cuyo contrato no ofrece SLA de latencia. Se mitiga con un circuit breaker y una cola de reintentos, pero no elimina la degradación percibida por el comercio.

Queda abierta la decisión sobre particionado del ledger por año fiscal. La propuesta inicial es particionar por rango de fechas y archivar en Object Storage tras 24 meses.

- R-01: indisponibilidad del adquirente (impacto alto, probabilidad media).
- R-02: crecimiento del ledger (impacto medio, probabilidad alta).
- D-01: particionado fiscal — pendiente de revisión con Finanzas.

---
