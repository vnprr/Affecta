# Plan Realizacji: Clinical RAG Agent dla Open WebUI

## Summary

- Dodajemy osobny serwis `clinical-rag-agent/` obok `open-webui/`, zamiast modyfikować wewnętrzny backend Open WebUI.
- Serwis jest FastAPI backendem z OpenAI-compatible API: `/v1/models` i `/v1/chat/completions`, dzięki czemu Open WebUI podpina go przez `OPENAI_API_BASE_URLS`.
- Pierwszy etap to funkcjonalne MVP: realny workflow czatu, RAG, warstwa antyhalucynacyjna, safety/crisis routing, cytacje i testy.
- Ciężkie elementy typu Neo4j, NLI i OCR są za adapterami albo w trybie degraded, aby pierwszy build był lekki.

## Key Changes

- `clinical-rag-agent/` zawiera moduły: `api/`, `agents/`, `services/`, `nlp/`, `rag/`, `graph/`, `safety/`, `schemas/`, `db/`, `observability/`, `tests/`.
- Rootowy `docker-compose.yml` uruchamia `open-webui`, `clinical-rag-agent` i `ollama`.
- Open WebUI jest skonfigurowane z `OPENAI_API_BASE_URLS=http://clinical-rag-agent:8000/v1`, `OPENAI_API_KEYS=local-dev-key`, `ENABLE_OPENAI_API=true` oraz `OLLAMA_BASE_URL=http://ollama:11434`.
- Serwis kliniczny ma `Dockerfile`, `.env.example`, `pyproject.toml`, `README.md` i ten plan.

## Implementation Changes

- API wystawia `/v1/models`, `/v1/chat/completions`, `/health`, `/metrics`, `/api/ingest` i `/api/sessions`.
- `AgentOrchestrator.handle_clinical_chat()` realizuje workflow: NLP analiza, risk check, RAG, Graph context, draft, hallucination validation, rewrite/fallback, judge i zapis sesji.
- Agenci podejmują decyzje, a serwisy wykonują pojedyncze operacje.
- `HallucinationService` agreguje `ClaimExtractor`, `EvidenceAlignment`, `CitationVerifier`, `ContradictionDetector`, `CertaintyClassifier`, `DelusionLanguageDetector` i `UnsupportedInferenceDetector`.
- MVP używa lokalnego persistent store w `data/`, lekkiego BM25 oraz hash embeddings bez pobierania ciężkich modeli.

## Problems Found And Fixes

- Plan źródłowy zakładał katalog `clinical-rag-agent/`, ale repo zawierało tylko `open-webui/`; dlatego serwis został dodany obok Open WebUI i spięty przez OpenAI-compatible API.
- Pełne NLI, OCR i Neo4j w pierwszym etapie zrobiłyby ciężki obraz; MVP używa adapterów i działa bez tych usług.
- Sam LLM judge nie wystarcza klinicznie; decyzję blokującą mają regułowe warstwy crisis, delusion validation, overconfident diagnosis i unsupported patient inference.
- Audit log nie zapisuje pełnych danych wrażliwych jako domyślnej ścieżki; sesje lokalne przechowują treść dla deweloperskiego MVP, a metryki zapisują tylko liczniki.

## Test Plan

- Unit tests obejmują claim extraction, evidence alignment, contradiction detection, citation verification, delusion validation, diagnostic certainty, crisis agent i RAG pipeline.
- Integration tests sprawdzają `/v1/models`, `/v1/chat/completions`, stream SSE, high-risk routing i zapis sesji.
- Docker smoke test: `docker compose up --build`, `http://localhost:8000/health`, model `clinical-rag-agent` widoczny w Open WebUI.

## Assumptions

- Pierwszy etap to funkcjonalne MVP, nie pełny produkcyjny system medyczny.
- Projekt ma charakter kliniczno-badawczy i wspierający, nie zastępuje diagnozy ani leczenia.
- Domyślny LLM provider to deterministyczny `stub`; produkcyjnie można użyć OpenAI-compatible adaptera przez zmienne środowiskowe.

