#!/usr/bin/env bash
set -e

API="http://localhost:8000"
DOC="tests/fixtures/golden_document.txt"

echo "1) Verificando que la API está viva..."
curl -sf "$API/health" | grep '"status":"ok"' && echo "  OK"

echo "2) Subiendo documento de referencia..."
INGEST_RESPONSE=$(curl -sf -X POST "$API/ingest" -F "file=@$DOC")
DOCUMENT_ID=$(echo "$INGEST_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['document_id'])")
echo "  document_id: $DOCUMENT_ID"

echo "3) Solicitando adaptación (perfil principiante, tutorial)..."
ADAPT_RESPONSE=$(curl -sf -X POST "$API/adapt" -H "Content-Type: application/json" \
  -d "{\"document_id\": \"$DOCUMENT_ID\", \"perfil\": \"principiante\", \"formato\": \"tutorial\", \"nivel_detalle\": \"estandar\"}")
JOB_ID=$(echo "$ADAPT_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "  job_id: $JOB_ID"

echo "4) Esperando resultado..."
for i in $(seq 1 20); do
  RESULT=$(curl -sf "$API/adapt/$JOB_ID")
  STATUS=$(echo "$RESULT" | python -c "import sys,json; print(json.load(sys.stdin).get('status'))")
  if [ "$STATUS" != "PROCESSING" ] && [ "$STATUS" != "QUEUED" ]; then
    break
  fi
  sleep 1
done
echo "  status final: $STATUS"

echo "5) Verificando contenido del resultado..."
echo "$RESULT" | python -c "
import sys, json
r = json.load(sys.stdin)
assert r['status'] in ('SUCCESS', 'PARTIAL', 'NO_CONTEXT'), 'status inesperado'
if r['status'] in ('SUCCESS', 'PARTIAL'):
    assert 'fidelity_score' in r['evaluacion_calidad']
    assert 'sources' in r['metadatos']
print('  Contenido y score de fidelidad presentes' if r['status'] != 'NO_CONTEXT' else '  NO_CONTEXT manejado correctamente')
"

echo ""
echo "=== MVP FUNCIONAL: VERIFICADO DE PUNTA A PUNTA ==="
