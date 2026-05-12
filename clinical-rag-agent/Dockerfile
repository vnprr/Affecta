# syntax=docker/dockerfile:1

ARG PYTHON_IMAGE=python:3.12-slim

FROM ${PYTHON_IMAGE} AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

COPY pyproject.toml README.md ./
COPY clinical_rag_agent ./clinical_rag_agent

RUN python -m pip install --upgrade pip && \
    python -m pip install --prefix=/install --no-cache-dir --no-compile .

RUN find /install -type d -name '__pycache__' -prune -exec rm -rf {} + && \
    find /install -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000 \
    CLINICAL_RAG_DATA_DIR=/app/data

WORKDIR /app

COPY --from=builder /install /usr/local

RUN mkdir -p /app/data && \
    find /usr/local -type d -name '__pycache__' -prune -exec rm -rf {} + && \
    find /usr/local -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete && \
    rm -rf /root/.cache /tmp/*

EXPOSE 8000

HEALTHCHECK CMD python -c "import json, os, urllib.request; data=json.load(urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/health', timeout=5)); raise SystemExit(0 if data.get('status') is True or data.get('status') == 'ok' else 1)"

CMD ["sh", "-c", "uvicorn clinical_rag_agent.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
