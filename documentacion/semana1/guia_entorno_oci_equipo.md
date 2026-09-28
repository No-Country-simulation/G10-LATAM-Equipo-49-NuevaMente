# Guía de configuración del entorno OCI — Equipo NuevaMente

**Alcance:** dejar a cada integrante capaz de **leer** los documentos del bucket de Object Storage.
**Cuándo usarla:** cuando el administrador de la tenancy ya creó tu usuario OCI, te agregó al grupo IAM de lectura y te entregó namespace, bucket y región.

---

## 0. Reglas de seguridad (léase primero)

1. Cada integrante usa **su propio usuario OCI** y **sus propias claves**. No se comparte `~/.oci/config` ni `~/.oci/keys`.
2. La clave privada **nunca** se sube a Git, nunca se envía por chat/email y nunca se pega en un PR.
3. Solo se comparte la **clave pública** (o su fingerprint) con el administrador.
4. El archivo `.env` del proyecto es local y ya está en `.gitignore`. Se versiona solo `.env.example`.
5. El bucket es de solo lectura para el equipo: nadie debe subir, borrar ni renombrar objetos.

Datos que debes recibir del administrador:

| Dato | Ejemplo | Uso |
| --- | --- | --- |
| OCID de usuario | `ocid1.user.oc1..aaaa...` | Identidad con la que te autenticas |
| OCID de tenancy | `ocid1.tenancy.oc1..aaaa...` | Tenancy de la cuenta |
| Región | `us-ashburn-1` | Región del bucket |
| Namespace | `axkf02paerjf` | Namespace de Object Storage |
| Bucket | `bucket-20260921-2152-nuevamente-docs-test` | Bucket a listar |
| Permisos | grupo IAM (p. ej. `nuevamente-oci-dev-readers`) | Permiso `read objects` |

---

## 1. Requisitos previos

- Linux, macOS o WSL en Windows.
- Python 3.10 o superior.
- `openssl` disponible.
- El repositorio clonado.

```bash
python3 --version
openssl version
```

---

## 2. Crear `~/.oci/keys` con permisos correctos

```bash
mkdir -p ~/.oci/keys
chmod 700 ~/.oci
chmod 700 ~/.oci/keys
```

Verificación:

```bash
ls -ld ~/.oci ~/.oci/keys
```

---

## 3. Generar el par de claves y el fingerprint

OCI autentica con un par RSA. Genera tu clave **en tu equipo**:

```bash
openssl genrsa -out ~/.oci/keys/oci_api_key.pem 4096
chmod 600 ~/.oci/keys/oci_api_key.pem
```

Extrae la clave pública y calcula su fingerprint (MD5 de la clave pública en DER), que es el valor que se registra en OCI:

```bash
openssl rsa -in ~/.oci/keys/oci_api_key.pem -pubout -out ~/.oci/keys/oci_api_key_public.pem 2>/dev/null
openssl rsa -pubin -in ~/.oci/keys/oci_api_key_public.pem -outform DER | openssl md5 -c
```

Guarda el resultado con este formato: `a1:b2:c3:d4:e5:f6:07:18:29:3a:4b:5c:6d:7e:8f:90:a1:b2:c3:d4`.

**Envía al administrador únicamente:** la clave pública `~/.oci/keys/oci_api_key_public.pem` o su fingerprint.

---

## 4. Crear `~/.oci/config`

```bash
nano ~/.oci/config
```

```ini
[DEFAULT]
user=ocid1.user.oc1..aaaaTUYBEXAMPLEUSERID
fingerprint=a1:b2:c3:d4:e5:f6:07:18:29:3a:4b:5c:6d:7e:8f:90:a1:b2:c3:d4
key_file=/home/tu_usuario/.oci/keys/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..aaaaEXAMPLETENANCYID
region=us-ashburn-1
```

```bash
chmod 600 ~/.oci/config
```

Notas:
- `key_file` debe ser la ruta **absoluta** a tu clave privada.
- Si tienes más de una identidad, define perfiles adicionales, por ejemplo `[nuevamente]`, y selecciona con `OCI_PROFILE`.
- La sección `[DEFAULT]` es obligatoria: el SDK la usa por defecto.

Prueba rápida de que la configuración es válida:

```bash
python3 -c "import oci, os; c=oci.config.from_file(os.path.expanduser('~/.oci/config')); print(c['region'], c['tenancy'])"
```

---

## 5. Entorno virtual de Python

Desde la raíz del repositorio:

```bash
cd /ruta/al/repositorio/G10-LATAM-Equipo-49-NuevaMente
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

En Windows (WSL/Git Bash) o si `source` no está disponible:

```bash
. .venv/bin/activate
```

Verifica que el entorno está activo (debe mostrar la ruta del `.venv`):

```bash
which python
pip --version
```

Desactivar el entorno al terminar:

```bash
deactivate
```

---

## 6. Instalar el SDK de OCI y las dependencias

```bash
pip install -r backend/requirements.txt
```

O, si solo necesitas el SDK para una prueba aislada:

```bash
pip install oci
```

Verificación:

```bash
python -c "import oci; print(oci.__version__)"
```

---

## 7. Configurar las variables del proyecto (`.env`)

```bash
cp .env.example .env
nano .env
```

```ini
OCI_CONFIG_FILE=~/.oci/config
OCI_PROFILE=DEFAULT
OCI_BUCKET_NAME=bucket-20260921-2152-nuevamente-docs-test
OCI_NAMESPACE=axkf02paerjf
OCI_PREFIX=
```

- `OCI_PREFIX` vacío = listar todo el bucket. Usa un prefijo (por ejemplo `docs-originales/`) si el administrador te asignó un subárbol.
- El `.env` se lee desde la **raíz del repositorio**, no desde `backend/`.
- Confirma que está ignorado por Git:

```bash
git check-ignore .env
```

Debe imprimir `.env`.

---

## 8. Verificar que puedes leer el bucket

### 8.1 Opción A — Script de listado

```bash
python bucket_test.py
```

Salida esperada: la lista de objetos con `name`, `size` y `Last Modified`, y el total.

### 8.2 Opción B — Endpoint del backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

En otra terminal:

```bash
curl "http://127.0.0.1:8000/test/oci/objects?limit=10"
```

Con filtro por prefijo:

```bash
curl "http://127.0.0.1:8000/test/oci/objects?prefix=docs-originales/&limit=10"
```

Respuesta esperada (`200`):

```json
{
  "bucket": "bucket-20260921-2152-nuevamente-docs-test",
  "namespace": "axkf02paerjf",
  "prefix": null,
  "count": 7,
  "next_start": null,
  "objects": [
    {
      "name": "docs-originales/Ejemplo.pdf",
      "size": 8294920,
      "etag": "186b4dba-638b-4916-8489-f1f24ca2edaa",
      "time_modified": "2026-09-22T03:54:33.663000+00:00"
    }
  ]
}
```

---

## 9. Errores frecuentes y solución

| Error | Causa | Solución |
| --- | --- | --- |
| `ConfigFileNotFound` | No existe `~/.oci/config` | Repite la sección 4 |
| `KeyNotFound` / `Could not find key_file` | Ruta de `key_file` incorrecta | Usa la ruta absoluta y confirma permisos `600` |
| `Signature verification failed` | Fingerprint o clave pública no coinciden | Regenera la clave pública y vuelve a registrar el fingerprint |
| `NotAuthorizedOrNotFound` (404/403) | Tu usuario no tiene permiso sobre el bucket | Pide al administrador que te agregue al grupo IAM con `read objects` |
| `bucket not found` | Nombre de bucket o namespace incorrecto | Verifica los valores en `.env` y la región en `~/.oci/config` |
| `OCI_NAMESPACE y OCI_BUCKET_NAME son obligatorios` | Faltan variables en `.env` | Revisa que el `.env` esté en la raíz del repo y completo |
| `size` y `time_modified` en `null` | Se pediu el listado sin `fields` | Usa el servicio del proyecto, que solicita `size,etag,timeCreated,timeModified` |

---

## 10. Buenas prácticas

- Verifica siempre los permisos con `ls -l ~/.oci/config ~/.oci/keys/oci_api_key.pem` (deben ser `600`).
- No edites `~/.oci/config` con permisos abiertos en una máquina compartida.
- Si necesitas más de 1000 objetos, pagina con el campo `next_start` devuelto por la respuesta.
- Si el administrador rota tu clave, repite las secciones 3 y 4 y elimina la clave anterior.
- Cuando termines de trabajar con el proyecto, ejecuta `deactivate`.
- En despliegues en OCI (VM/Compute), no uses claves locales: configura **Instance Principal**.
