# Clinical RAG Agent

OpenAI-compatible FastAPI backend for Open WebUI. The service exposes `/v1/models` and `/v1/chat/completions`, so Open WebUI can use it as an external provider.

The system includes an NLP-based anti-hallucination layer that validates generated responses before they are shown to the user. It extracts clinical claims, checks them against retrieved evidence, verifies citations, detects contradictions with patient context, identifies unsupported patient-specific inferences, and prevents overconfident diagnostic statements or validation of delusional beliefs.

This layer works together with RAG, Graph RAG, and a separate judge step to reduce hallucinations and improve clinical safety.

## Current MVP Direction

The current implemented focus is a therapeutic session agent:

Open WebUI -> therapeutic session agent -> session memory -> therapy state -> RAG-assisted context -> validation -> stored session notes.

The user-facing assistant should feel like an ongoing therapeutic support conversation. Diagnostic and clinical components guide internal reasoning, but visible responses should not become diagnostic reports.

Graph RAG, OCR, a human review panel, and production-grade external vector stores remain later roadmap items.

### Step 2: Therapeutic Session Notes

The system creates an internal therapeutic session note after each user/assistant exchange. These notes are not visible to the user. They store the therapeutic significance of the exchange, key emotions, themes, recurring patterns, open threads, suggested next focus and possible human review flags. This allows Affecta to behave like an ongoing therapeutic process rather than a stateless chatbot.

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
