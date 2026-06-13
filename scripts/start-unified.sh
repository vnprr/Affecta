#!/usr/bin/env bash
set -euo pipefail

export PORT="${PORT:-8080}"
export HOST="${HOST:-0.0.0.0}"
export CLINICAL_RAG_HOST="${CLINICAL_RAG_HOST:-127.0.0.1}"
export CLINICAL_RAG_PORT="${CLINICAL_RAG_PORT:-9000}"
export CLINICAL_RAG_API_KEY="${CLINICAL_RAG_API_KEY:-local-dev-key}"
export CLINICAL_RAG_DATA_DIR="${CLINICAL_RAG_DATA_DIR:-/app/backend/data/clinical-rag-agent}"
export ENABLE_OPENAI_API="${ENABLE_OPENAI_API:-true}"
export OPENAI_API_BASE_URLS="${OPENAI_API_BASE_URLS:-http://${CLINICAL_RAG_HOST}:${CLINICAL_RAG_PORT}/v1}"
export OPENAI_API_KEYS="${OPENAI_API_KEYS:-$CLINICAL_RAG_API_KEY}"
export WEBUI_SECRET_KEY="${WEBUI_SECRET_KEY:-${WEBUI_JWT_SECRET_KEY:-}}"

mkdir -p "$CLINICAL_RAG_DATA_DIR" /app/backend/data

if [[ "${USE_OLLAMA_DOCKER,,}" == "true" ]]; then
  export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
  export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
fi

python -m uvicorn clinical_rag_agent.main:app \
  --host "$CLINICAL_RAG_HOST" \
  --port "$CLINICAL_RAG_PORT" &
clinical_pid=$!

for _ in $(seq 1 60); do
  if curl -fsS "http://${CLINICAL_RAG_HOST}:${CLINICAL_RAG_PORT}/health" >/dev/null; then
    break
  fi
  sleep 1
done

if ! curl -fsS "http://${CLINICAL_RAG_HOST}:${CLINICAL_RAG_PORT}/health" >/dev/null; then
  echo "clinical-rag-agent failed to become healthy" >&2
  kill "$clinical_pid" 2>/dev/null || true
  exit 1
fi

cd /app/backend
exec bash start.sh
