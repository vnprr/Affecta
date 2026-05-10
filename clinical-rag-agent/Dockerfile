FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CLINICAL_RAG_DATA_DIR=/app/data

WORKDIR /app

COPY pyproject.toml README.md ./
COPY clinical_rag_agent ./clinical_rag_agent

RUN pip install --no-cache-dir .

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "clinical_rag_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]

