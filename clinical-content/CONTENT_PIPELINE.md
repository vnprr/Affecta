# Content Pipeline — from draft to live

This describes the lifecycle of a clinical document and the **definition of done**.

## Stages

1. **Draft** — A clinical author copies the right template from `templates/` into the
   correct `methods/<method>/` folder, renames it to `<id>.md`, and writes the content.
2. **Self-check** — The author runs the quality checklist in `AUTHORING_GUIDE.md` §9.
3. **Clinical review** — A senior psychologist reviews against the same checklist and
   either accepts or returns with comments. Reviewer records acceptance in the PR/commit.
4. **Ingestion** — An engineer runs `tools/build_chunks.py` to convert accepted
   documents into retrieval records and loads them (see below).
5. **Live** — The content is retrievable by the agent's RAG layer.

## Definition of done (per document)

- Passes the full quality checklist.
- Uses only taxonomy terms for `method`, `domain`, `links_patterns`, `links_hypotheses`.
- Has a unique, permanent `id`.
- Has at least one real citation in `sources` (clinician docs and clinical claims).
- Clinical reviewer has signed off.

## How documents become retrievable

The running service stores knowledge as JSON Lines chunks in
`clinical-rag-agent/data/rag/chunks.jsonl`, and exposes an ingestion endpoint
`POST /api/ingest` that accepts documents of this shape:

```json
{
  "source": "<id from front matter>",
  "title": "<title>",
  "text": "<body text>",
  "metadata": {"method": "CBT", "domain": "anxiety", "audience": "clinician",
               "evidence_level": "strong", "tags": "cbt,cognition"}
}
```

`tools/build_chunks.py` parses each accepted `.md`, maps its front matter to this
shape (the body becomes `text`; all other fields go into `metadata` as strings),
and can either:

- print a `documents.json` array (for review), or
- POST directly to the ingestion API.

Example:

```bash
# dry run: emit the documents JSON the API would receive
python clinical-content/tools/build_chunks.py clinical-content/methods --out documents.json

# load into a running service
python clinical-content/tools/build_chunks.py clinical-content/methods \
    --api http://localhost:8000 --token local-dev-key
```

> Note (current MVP): retrieval uses a lightweight local matcher and the `metadata`
> filters are stored but not yet used to scope retrieval. Authoring with correct
> metadata now means no rework when filtered retrieval and richer embeddings land
> (see the main plan's RAG roadmap). Keep documents single-purpose so each retrieved
> chunk is self-contained.

## Versioning and changes

- To revise content, edit the same file and keep the same `id`. Re-ingest.
- To retire content, remove the file and re-run a full ingest into a fresh
  `chunks.jsonl` (ingestion appends, so a clean rebuild is how deletions take effect).
- Record substantive clinical changes in the commit message and re-trigger review.
