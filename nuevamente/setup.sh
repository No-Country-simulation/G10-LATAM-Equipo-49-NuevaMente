#!/usr/bin/env bash
cd "$(dirname "$0")" && python3 -m venv .venv && source .venv/bin/activate \
  && pip install -r backend/requirements.txt \
  && echo "Instalacion terminada. Usa ./run_api.sh y ./run_ui.sh"
