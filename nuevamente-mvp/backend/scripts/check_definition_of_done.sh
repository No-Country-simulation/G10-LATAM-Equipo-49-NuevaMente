#!/usr/bin/env bash
set -e

echo "== 1. El código compila/ejecuta =="
python -c "import src.api.main" && echo "OK: import de la app exitoso"

echo "== 2. Lint sin errores =="
ruff check src/ tests/

echo "== 3. Tests en verde =="
pytest tests/ -q

echo "== 4. .env.example está actualizado (sin secretos) =="
if grep -E "GEMINI_API_KEY=.+|OCI_.*KEY.*=.+" ../.env.example; then
  echo "FALLO: hay valores no vacíos en variables sensibles de .env.example"
  exit 1
fi
echo "OK: .env.example sin secretos"

echo "== 5. Ninguna key hardcodeada en el código =="
if grep -rniE "AIzaSy|-----BEGIN (RSA|PRIVATE) KEY-----" src/; then
  echo "FALLO: posible secreto hardcodeado"
  exit 1
fi
echo "OK: sin secretos hardcodeados"

echo "== Definition of Done: TODO VERDE =="
