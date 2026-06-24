# Affecta — Therapist Panel (Human-in-the-Loop)

A standalone, zero-build supervision panel for a human reviewer (e.g. a supervising
therapist). It talks directly to the `clinical-rag-agent` HTTP API and lets a
reviewer inspect a case and steer the agent.

## What it shows / does

- **Sessions list** and per-session case overview (stage, count, active focus,
  presenting problems, recurring patterns, longitudinal summary).
- **Working hypotheses** (internal) with **Approve** / **Reject** — a decision is
  persisted on the case state and immediately changes how future sessions behave
  (rejected hypotheses are no longer used to guide the agent; approved ones become
  `confirmed_by_human` / high confidence).
- **Therapy goals** — pause, complete, or flip a goal between *visible* and
  *internal*.
- **Session notes** with a "needs attention" flag surfaced for review.
- **Reviewer actions** — add a free-text note and override the active focus.
- **Bilingual UI** — switch between English and Polish (top-right selector).

## Running

It is a single static file. Open it directly, or serve it:

```bash
cd therapist-panel
python -m http.server 5500
# open http://localhost:5500
```

In the top bar set:

- **API URL** — the `clinical-rag-agent` base URL (default `http://localhost:8000`).
- **API token** — the bearer token (`CLINICAL_RAG_API_KEY`, default `local-dev-key`).

Then click **Load sessions**.

> Note: the panel is a deliberately simple academic tool. For a real deployment,
> serve it over HTTPS, use a real reviewer identity instead of a shared token, and
> restrict CORS origins on the backend (`CLINICAL_RAG_ALLOWED_ORIGINS`).

## API used

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/sessions` | list sessions |
| GET | `/api/sessions/{id}/therapy-state` | case state |
| GET | `/api/sessions/{id}/notes` | session notes |
| POST | `/api/sessions/{id}/human-decision` | approve/reject a hypothesis |
| POST | `/api/sessions/{id}/active-focus` | override active focus |
| POST | `/api/sessions/{id}/human-review-note` | add a reviewer note |
| PATCH | `/api/sessions/{id}/goals/{goal_id}` | update goal status/visibility |
