#!/usr/bin/env bash
# Guion de prueba automatizado - RAG + LLM Real (/ingest -> /adapt -> polling)

set -e

BASE_URL="http://127.0.0.1:8000"
FIXTURE_FILE="backend/tests/fixtures/sample_contenedores.md"

echo "=== [1/4] Smoke Test: Verificando estado del servidor ==="
HEALTH_RESP=$(curl -s -X GET "${BASE_URL}/health")
echo "Respuesta /health: ${HEALTH_RESP}"
echo ""

if [[ ! -f "${FIXTURE_FILE}" ]]; then
    echo "❌ Error: No se encontró el archivo de prueba en ${FIXTURE_FILE}"
    exit 1
fi

echo "=== [2/4] Ingesta: Subiendo ${FIXTURE_FILE} ==="
INGEST_RESP=$(curl -s -X POST "${BASE_URL}/ingest" \
  -F "file=@${FIXTURE_FILE}")

echo "Respuesta /ingest: ${INGEST_RESP}"

# Extraer document_id
DOC_ID=$(echo "${INGEST_RESP}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('document_id', ''))")

if [[ -z "${DOC_ID}" ]]; then
    echo "❌ Error: No se obtuvo document_id de /ingest"
    exit 1
fi
echo "✅ document_id obtenido: ${DOC_ID}"
echo ""

echo "=== [3/4] Adaptación: Solicitando adaptación asíncrona ==="
ADAPT_RESP=$(curl -s -X POST "${BASE_URL}/adapt" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "'"${DOC_ID}"'",
    "perfil": "Principiante / Transición de Carrera",
    "formato": "Guía Práctica Paso a Paso (Tutorial)",
    "nicho": "Fintech"
  }')

echo "Respuesta /adapt: ${ADAPT_RESP}"

# Extraer job_id
JOB_ID=$(echo "${ADAPT_RESP}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))")

if [[ -z "${JOB_ID}" ]]; then
    echo "❌ Error: No se obtuvo job_id de /adapt"
    exit 1
fi
echo "✅ job_id obtenido: ${JOB_ID}"
echo ""

echo "=== [4/4] Polling: Consultando estado hasta finalizar ==="
STATUS="PROCESSING"
ATTEMPTS=0
MAX_ATTEMPTS=20

while [[ "${STATUS}" == "PROCESSING" || "${STATUS}" == "QUEUED" ]]; do
    if [[ ${ATTEMPTS} -ge ${MAX_ATTEMPTS} ]]; then
        echo "❌ Timeout: El job no finalizó a tiempo."
        exit 1
    fi

    sleep 3
    ATTEMPTS=$((ATTEMPTS+1))

    JOB_RESP=$(curl -s -X GET "${BASE_URL}/adapt/${JOB_ID}")
    STATUS=$(echo "${JOB_RESP}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))")
    echo "Consulta #${ATTEMPTS} - Status actual: ${STATUS}"
done

echo ""
echo "========================================================================="
echo "RESULTADO FINAL DE LA ADAPTACION (status: ${STATUS}):" -ForegroundColor Yellow
echo "========================================================================="
echo "${JOB_RESP}" | python3 -m json.tool