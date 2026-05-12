FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    CLINICAL_RAG_DATA_DIR=/app/data

WORKDIR /app

COPY pyproject.toml README.md ./
COPY clinical_rag_agent ./clinical_rag_agent

RUN pip install --no-cache-dir .

RUN mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK CMD python -c "import json, os, urllib.request; data=json.load(urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/health', timeout=5)); raise SystemExit(0 if data.get('status') is True or data.get('status') == 'ok' else 1)"

CMD ["sh", "-c", "uvicorn clinical_rag_agent.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
