#!/usr/bin/env bash
cd "$(dirname "$0")" && source .venv/bin/activate && cd backend \
  && python -m uvicorn src.api.main:app --port 8000
