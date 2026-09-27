#!/usr/bin/env bash
set -e

# Automatically activate virtualenv if not already in PATH
if [ -d "/app/.venv" ] && [[ ":$PATH:" != *":/app/.venv/bin:"* ]]; then
    export PATH="/app/.venv/bin:$PATH"
fi

export PYTHONPATH="${PYTHONPATH:-/app/src:/app/scripts}"
export HF_HOME="${HF_HOME:-/app/.cache/huggingface}"

# Ensure cache/data directories exist
mkdir -p "$HF_HOME" /app/artifacts /app/adapters

# 1. Download/verify model & adapter unless explicitly skipped
if [ "${SKIP_MODEL_DOWNLOAD:-0}" != "1" ] && [ "${SKIP_MODEL_DOWNLOAD:-false}" != "true" ]; then
    echo "===> Checking and preparing base model and adapter..."
    python scripts/prepare_models.py \
        --model-size "${MODEL_SIZE:-2b}" \
        --adapter-repo "${HF_ADAPTER_REPO:-mohit67890/imajev-2b}" \
        --adapter-dir "${ADAPTER:-adapters/imajev-2b}"
fi

# 2. Check if a custom command was passed
if [ "$#" -gt 0 ] && [ "${1:0:1}" != "-" ]; then
    exec "$@"
fi

# 3. Default: start imajev server
echo "===> Starting imajev server on 0.0.0.0:${PORT:-8765}..."
exec python scripts/playground/server.py \
    --host "0.0.0.0" \
    --port "${PORT:-8765}" \
    --backend "${BACKEND:-torch}" \
    --adapter "${ADAPTER:-adapters/imajev-2b}" \
    --calibration "${CALIBRATION:-adapters/imajev-2b/calibration.json}" \
    --model-name "${MODEL_NAME:-imajev-2b}" \
    "$@"
