#!/usr/bin/env bash
set -e

echo "=== NuevaMente — Guion de demo ==="

echo "[1/4] Levantando backend..."
(cd backend && uvicorn src.api.main:app --port 8000 &)
sleep 3

echo "[2/4] Smoke test (GET /health)..."
curl -sf http://localhost:8000/health || { echo "Backend no responde"; exit 1; }

echo "[3/4] Levantando interfaz web..."
(cd ui && streamlit run app.py &)
sleep 3

echo "[4/4] Todo listo."
echo "Abrir http://localhost:8501 y seguir docs/demo-scenarios/escenario-1-principiante.md"
