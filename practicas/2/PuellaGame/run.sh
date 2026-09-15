#!/usr/bin/env bash
# Inicia el prototipo en local: crea el entorno virtual si hace falta,
# instala las dependencias y arranca uvicorn.
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
PORT="${PORT:-8000}"
VENV=".venv"

[ -d "$VENV" ] || "$PYTHON" -m venv "$VENV"

source "$VENV/bin/activate"

pip install -q -r requirements.txt

exec python -m uvicorn app:app --host 127.0.0.1 --port "$PORT"
