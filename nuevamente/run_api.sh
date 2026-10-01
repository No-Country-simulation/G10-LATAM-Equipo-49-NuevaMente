#!/usr/bin/env bash
# Enciende la API en http://127.0.0.1:8000  (documentación en /docs)
cd "$(dirname "$0")"
[ -d .venv ] || { echo "Primero ejecuta ./setup.sh"; exit 1; }
source .venv/bin/activate
cd backend
exec python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
