#!/usr/bin/env bash
# Instala todo lo necesario (una sola vez).
set -e
cd "$(dirname "$0")"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' \
  || { echo "Se necesita Python 3.11 o superior."; exit 1; }
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
echo "Instalacion terminada. Ahora ejecuta ./run_api.sh"
