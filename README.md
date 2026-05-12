# Affecta

**Affecta** to agentowy system RAG + LLM wspierający wywiad psychologiczny, analizę rozmowy, psychoedukację oraz tworzenie planu pracy terapeutycznej pod nadzorem specjalisty. Projekt łączy klasyczne NLP, RAG dokumentowy, Graph RAG, LLM Judge oraz monitoring systemu.

## Główne funkcje

- prowadzenie ustrukturyzowanego wywiadu psychologicznego,
- rozmowa z użytkownikiem w trybie sesji wspierającej,
- analiza emocji, intencji, ryzyka i stylu komunikacji,
- tworzenie hipotez klinicznych bez stawiania ostatecznej diagnozy,
- przygotowywanie planu dalszej pracy terapeutycznej,
- wykrywanie treści kryzysowych i ryzykownych,
- krytyczne reagowanie na treści urojeniowe bez ich wzmacniania,
- korzystanie z literatury naukowej przez RAG,
- obsługa klasycznego RAG oraz Graph RAG,
- upload PDF, OCR PDF oraz obrazów do bazy wiedzy,
- wielowarstwowa walidacja odpowiedzi przeciw halucynacjom,
- ocena odpowiedzi przez osobnego LLM Judge,
- możliwość pracy przez OpenRouter lub lokalny model,
- integracja z Open WebUI,
- monitoring przez Prometheus i Grafana.

## Agenci

- **Intake Agent** — prowadzi wywiad i zbiera podstawowe informacje.
- **Session Agent** — prowadzi rozmowę w ramach sesji.
- **Diagnostic Hypothesis Agent** — tworzy ostrożne hipotezy kliniczne.
- **Treatment Plan Agent** — proponuje plan pracy terapeutycznej.
- **Crisis Agent** — wykrywa sytuacje kryzysowe i uruchamia procedury bezpieczeństwa.
- **Delusion Detection Agent** — wykrywa treści urojeniowe i zapobiega ich wzmacnianiu.
- **RAG Agent** — pobiera wiedzę z dokumentów i źródeł naukowych.
- **Graph RAG Agent** — korzysta z grafu objawów, zaburzeń, interwencji i źródeł.
- **Hallucination Guard Agent** — sprawdza, czy odpowiedź ma pokrycie w danych.
- **Judge Agent** — ocenia końcową odpowiedź przed pokazaniem jej użytkownikowi.

## Główne serwisy

- **LLM Service** — obsługa OpenRouter i lokalnych modeli.
- **RAG Service** — wyszukiwanie w bazie wektorowej.
- **Graph Service** — zapytania do grafu wiedzy.
- **NLP Service** — analiza tekstu, intencji, emocji i ryzyka.
- **Hallucination Service** — wykrywanie niepopartych twierdzeń.
- **Citation Service** — sprawdzanie źródeł i cytowań.
- **Ingestion Service** — upload i przetwarzanie plików.
- **OCR Service** — ekstrakcja tekstu z PDF i obrazów.
- **Safety Service** — kontrola odpowiedzi i procedury bezpieczeństwa.
- **Monitoring Service** — metryki systemu dla Prometheus/Grafana.

## Przebieg działania

1. Użytkownik rozpoczyna rozmowę w Open WebUI.
2. Backend FastAPI odbiera wiadomość przez endpoint zgodny z OpenAI API.
3. NLP Service analizuje intencję, emocje, ryzyko i ważne encje.
4. Crisis Agent sprawdza, czy występuje zagrożenie wymagające reakcji bezpieczeństwa.
5. Intake Agent lub Session Agent prowadzi rozmowę zależnie od etapu sesji.
6. RAG Agent pobiera wiedzę z dokumentów, PDF, OCR i źródeł zewnętrznych.
7. Graph RAG Agent uzupełnia kontekst relacjami między objawami, hipotezami i interwencjami.
8. Diagnostic Hypothesis Agent tworzy ostrożne hipotezy do weryfikacji.
9. Treatment Plan Agent proponuje ogólny plan pracy terapeutycznej.
10. Hallucination Guard Agent sprawdza zgodność odpowiedzi ze źródłami i rozmową.
11. Judge Agent ocenia bezpieczeństwo, ton i poprawność odpowiedzi.
12. Zweryfikowana odpowiedź trafia do użytkownika.
13. System zapisuje metryki, logi i dane sesji do dalszej analizy.

## Założenia bezpieczeństwa

Affecta nie zastępuje psychologa, psychiatry ani psychoterapeuty. System tworzy hipotezy i materiały wspierające, ale nie stawia ostatecznych diagnoz, nie przepisuje leków i nie prowadzi samodzielnego leczenia. Odpowiedzi kliniczne wymagają nadzoru oraz weryfikacji przez specjalistę.

## Planowany stack

- Open WebUI
- FastAPI
- OpenRouter
- lokalny model LLM jako opcja
- Qdrant / pgvector
- Neo4j
- PostgreSQL
- Docker
- Prometheus
- Grafana
- OCR: Tesseract, PaddleOCR, EasyOCR
