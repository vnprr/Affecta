# Clinical RAG Agent

OpenAI-compatible FastAPI backend for Open WebUI. The service exposes `/v1/models` and `/v1/chat/completions`, so Open WebUI can use it as an external provider.

The system includes an NLP-based anti-hallucination layer that validates generated responses before they are shown to the user. It extracts clinical claims, checks them against retrieved evidence, verifies citations, detects contradictions with patient context, identifies unsupported patient-specific inferences, and prevents overconfident diagnostic statements or validation of delusional beliefs.

This layer works together with RAG, Graph RAG, and a separate judge step to reduce hallucinations and improve clinical safety.

## Run

From the repository root:

```bash
docker compose up --build
```

Open WebUI will be available at `http://localhost:3000`, and this backend at `http://localhost:8000`.

## Development

```bash
cd clinical-rag-agent
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn clinical_rag_agent.main:app --reload
```

## Safety Scope

This MVP is a clinical research/support scaffold. It does not diagnose, prescribe, or replace professional care. Crisis and self-harm language is routed to a crisis response before RAG or generation.

