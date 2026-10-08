# Bloqueo para desplegar la VM en OCI y alternativas de hospedaje — Semana 2

**Fecha:** 2026-09-28
**Autor:** equipo cloud (Rol OCI)
**Estado:** DECISIÓN PENDIENTE — requiere confirmación del equipo antes de avanzar
**Objetivo:** registrar el bloqueo técnico de OCI Compute, demostrar que no es un problema
de configuración del lado del equipo, y proponer las dos alternativas viables para hospedar
el servidor (backend + n8n + Streamlit) sin comprometer la demo final.

---

## 1. Resumen ejecutivo

| Ítem | Estado |
| --- | --- |
| Instancia OCI Compute (Ampere A1 Flex, capa Always Free) en `us-ashburn-1` | **Bloqueada** — `Out of host capacity` |
| Duración del bloqueo | ~2 días de reintentos automatizados, sin éxito |
| Causa | Saturación de capacidad de la shape en el data center (problema del lado de OCI) |
| ¿Es problema de configuración del equipo? | **No** |
| ¿Se puede esquivar cambiando de región? | **No** — cuentas Always Free están suscritas a una sola región |
| Requisito obligatorio de OCI en el hackathon | **Object Storage únicamente** — cumplido e independiente de la VM |
| Recomendación | **Opción A (AWS con créditos personales)** para la demo, laptop como respaldo |

**Conclusión:** el checklist obligatorio del hackathon se puede cumplir al 100 % sin la VM en OCI.
Lo que se pierde es únicamente el punto diferencial de "todo en OCI".

---

## 2. Situación

El objetivo de infraestructura era crear la instancia de cómputo **Ampere A1 Flex** (la que corresponde
a la capa **Always Free** del Free Tier de OCI) en la región donde ya está el bucket del equipo
(`us-ashburn-1`, bucket `bucket-20260921-2152-nueivamente-docs-test`).

La creación de la instancia ha fallado de forma consistente desde el 2026-09-26 con el error:

```
Out of host capacity
```

### 2.1 Naturaleza del error

| Pregunta | Respuesta |
| --- | --- |
| ¿Es un problema de nuestra configuración ( tenancy, límites, subnet, AD, imagen)? | **No** |
| ¿Es un problema reportado por otros usuarios de OCI Free Tier? | **Sí**, es un Incidente conocido de saturación de la shape `VM.Standard.A1.Flex` |
| ¿Es transitorio (puede resolverse solo)? | Probablemente sí a corto plazo, pero **sin garantía de plazo** |
| ¿Podemos escalarlo a soporte de OCI? | Sí, pero el Free Tier no tiene SLA de capacidad y la respuesta no compromete fecha |

La diferencia con un error de configuración es que el mismo script, con la misma configuración, **sí crea
instancias de otras shapes**. El rechazo ocurre únicamente en la asignación de hosts `Ampere A1`, lo que
apunta a un cuello de botella del data center y no a la cuenta.

### 2.2 Evidencia: reintento automatizado durante ~2 días

Para descartar que fuera un evento puntual, se dejó corriendo un script que reintenta la creación de la
instancia **cada minuto** durante casi 2 días consecutivos.

| Métrica | Valor |
| --- | --- |
| Duración del reintento | ~2 días (≈2.880 intentos a 1/min) |
| Intentos exitosos | **0** |
| Errores distintos de `Out of host capacity` | 0 (el único error observado es el de capacidad) |
| Cambios aplicados a la configuración durante el periodo | Ninguno |

Un volumen de 0 éxitos en ~2.880 intentos con configuración constante confirma que **no es un problema
puntual ni de configuración**, sino una restricción sostenida de capacidad.

### 2.3 Por qué no se puede cambiar de región

Se evaluó ejecutar el despliegue en otra región con capacidad disponible. **Descartado** por la propia
regla de Oracle Free Tier:

| Restricción | Implicación |
| --- | --- |
| Una cuenta **Always Free** está suscrita a **una sola región** de por vida | Cambiar de región implica **perder la suscripción actual** |
| Recrear la cuenta en otra región no está garantizado | Tampoco existe garantía de que la nueva región tenga capacidad libre en la shape A1 |
| El bucket `bucket-20260921-2152-nuevamente-docs-test` vive en `us-ashburn-1` | Cambiar de región obligaría a migrar también Object Storage y rehacer las políticas IAM |

Es decir: cambiar de región tiene un costo alto (pérdida de la cuenta Always Free) con una probabilidad
de éxito no mayor que la de esperar a que se libere capacidad en la región actual.

---

## 3. Aclaración sobre los requisitos del hackathon

Revisando la documentación oficial del hackathon, el único requisito **obligatorio** relacionado con
OCI es **Object Storage**, usado para persistir los documentos originales y el contenido generado.

| Recurso de OCI | Clasificación en el checklist | ¿Depende de la VM? |
| --- | --- | --- |
| **OCI Object Storage** (bucket de documentos originales y contenido generado) | **OBLIGATORIO** | **No** |
| OCI Compute Instance — "Despliegue Completo en la Nube" | **Opcional / diferencial** | Sí |

**Implicación directa:** se puede cumplir el **100 % del checklist obligatorio** sin que la VM corra
dentro de OCI. Lo único que se deja de sumar es el punto extra específico de "todo en OCI".

> **Invariante que este documento propone no romper:** ningún componente del pipeline debe asumir
> que corre dentro de OCI. El acceso a Object Storage es **tráfico HTTPS contra el endpoint público de
> OCI**, por lo que funciona idénticamente desde AWS, desde una laptop, o desde cualquier otra nube.

---

## 4. Alternativas para hospedar el servidor

Componentes a hospedar: **backend (FastAPI) + n8n + Streamlit**.

### 4.1 Opción A — AWS (usando créditos personales disponibles)

| Criterio | Evaluación |
| --- | --- |
| Disponibilidad | ✅ Sin lucha por capacidad: la instancia se crea sin espera |
| Potencia | ✅ Instancia más potente que la buscada en OCI |
| Compatibilidad con OCI Object Storage | ✅ Trivial — HTTPS normal al endpoint de OCI, sin importar desde qué nube salga el tráfico |
| Costo | ⚠️ Corre con **créditos personales** — estimado **~$50 USD** para todo el periodo del hackathon (pruebas + demo final) |
| Control de gasto | ⚠️ Mitigable: mantener la instancia **detenida** cuando no se use (EC2 cobra por instancia en ejecución, no por almacenamiento) |
| Administración | ⚠️ Requiere que alguien administre la cuenta de AWS (el autor de esta propuesta tiene experiencia y se encarga) |
| Riesgo de cuota | ⚠️ Bajo: los créditos personales de capa gratuita no tienen el cuello de botella de capacidad de OCI |

**Veredicto:** es la opción más confiable para la demo final.

### 4.2 Opción B — Servidor local (laptop propia)

| Criterio | Evaluación |
| --- | --- |
| Costo | ✅ Costo cero |
| Exposición a internet | ⚠️ Depende de si el proveedor de internet asigna **IP pública**. Si no, se resuelve con **Cloudflare Tunnel** (herramienta gratuita), pero añade un paso extra de configuración |
| Disponibilidad | ⚠️ **Riesgo real:** depende de que la conexión y la infraestructura no fallen justo el día de la demo. Este riesgo no existe en la nube |
| Escalabilidad | ⚠️ Sin margen si el uso crece |

**Veredicto:** viable como entorno de desarrollo y respaldo, no recomendable como única opción para la demo.

### 4.3 Comparación lado a lado

| Criterio | Opción A (AWS) | Opción B (Laptop) | OCI A1 (bloqueada) |
| --- | --- | --- | --- |
| Probabilidad de estar operativo el día de la demo | **Alta** | Media | **Muy baja** (sin plazo) |
| Costo para el equipo | ~$50 USD (créditos personales) | $0 | $0 (Always Free) |
| Cuenta a odorar | 1 persona (autor) | 1 persona (autor) | 1 persona (autor) |
| Riesgo de caída en vivo | Bajo | **Alto** (dependencia de red local) | N/A (no existe instancia) |
| Cumplimiento de obligatorios OCI | ✅ (Object Storage intacto) | ✅ (Object Storage intacto) | ✅ |
| Punto diferencial "todo en OCI" | ❌ | ❌ | ✅ (cuando se libere) |

---

## 5. Recomendación y plan de acción

### 5.1 Decisión propuesta

1. **Ir con la Opción A (AWS)** por ser la más confiable para la demo final.
2. **Dejar la laptop como entorno de respaldo/desarrollo** mientras tanto (Opción B como plan de contingencia).
3. **Seguir intentando en OCI en paralelo** por si se libera capacidad antes del fin de semana — **no sería un
   cambio definitivo**, sino un plan B adicional si logramos la VM a tiempo.
4. **No bloquear el roadmap técnico** por esta decisión: el pipeline no debe tener dependencia de dónde corre.

### 5.2 Qué NO depende de esta decisión

Estos puntos del backlog se pueden avanzar hoy mismo, con cualquiera de las opciones:

- Implementación de ingesta, chunking, embeddings, RAG, generación y validación.
- Persistencia en **OCI Object Storage** (ya es el requisito obligatorio y ya funciona: 7 objetos listados y leídos).
- Orquestación con n8n y UI con Streamlit ejecutándose en local durante el desarrollo.
- Configuración por entorno (`.env`) con la misma variable `OCI_BUCKET_NAME` / `OCI_NAMESPACE` /
  `OCI_REGION` sin importar el host.

### 5.3 Condiciones de seguridad que se mantienen en todas las opciones

- El bucket permanece en OCI **Always Free**: no se migra a AWS.
- Las credenciales de OCI siguen siendo **por integrante**, nunca compartidas (ver
  `semana1/guia_entorno_oci_equipo.md`, sección 0).
- En cualquier host que no sea la laptop de un integrante (AWS, VM), la autenticación hacia OCI debe usar
  **Instance Principal** en lugar de claves locales, o un mecanismo equivalente sin secretos en disco.
- `.env` y `*.pem` fuera de Git en todos los entornos.

---

## 6. Riesgos abiertos

| # | Riesgo | Severidad | Mitigación |
| --- | --- | --- | --- |
| R1 | La capacidad de OCI A1 no se libere antes del fin de semana | Media | Ninguna: se asume que seguirá bloqueada; por eso se recomienda AWS |
| R2 | Descuadre entre el presupuesto de créditos personales y la estimación de ~$50 | Baja | Instancia detenida fuera de las ventanas de prueba y demo; alerta de presupuesto activa |
| R3 | La demo en vivo falle por dependencia de la red local (si se cae a Opción B) | **Alta** | Evitar Opción B como único plan; tener la instancia de AWS en marcha y verificada el día anterior |
| R4 | Que "todo en OCI" se interprete como obligatorio por los jueces | Media | Este documento deja constancia de la clasificación oficial (opcional/diferencial) y del cumplimiento completo de Object Storage |
| R5 | Que el cambio de host introduzca diferencias de entorno (IPs, DNS, CORS) | Media | Configuración por entorno y pruebas de integración en el host definitivo antes de la demo |

---

## 7. Decisión solicitada al equipo

Se solicita confirmación de una de las siguientes:

- [ ] **Opción A aprobada** — AWS con créditos personales como entorno de demo; laptop como respaldo.
- [ ] **Opción B aprobada** — laptop como servidor único, asumiendo el riesgo de disponibilidad.
- [ ] **Aprobación condicionada** — se espera hasta el lunes X a la liberación de capacidad en OCI, y si no
      ocurre, se aplica Opción A.
- [ ] **Otra alternativa** — se propone y se evalúa.

**Responsable de ejecutar la opción aprobada:** pendiente de asignar.
**Fecha límite de decisión:** pendiente de fijar (recomendado: antes del cierre de la Semana 2).

---

## 8. Evidencia y referencias

- Script de reintento de creación de instancia ejecutándose cada minuto durante ~2 días (registro en consola
  del rol cloud).
- Guía de entorno OCI del equipo: `documentacion/semana1/guia_entorno_oci_equipo.md`
  (reglas de credenciales, `Instance Principal` para despliegues, datos del bucket).
- Análisis de estructura de la rama `proposal/v1`: `documentacion/semana2/analisis_estructura_proposal_v1.md`
  (COMP-09 `storage/oci_client.py` como punto de integración del StorageClient).
- Cambios y brechas de Semana 1: `documentacion/semana1/cambios_rama_develop.md`
  (OCI-001 marcado como completado vía listado del bucket).
