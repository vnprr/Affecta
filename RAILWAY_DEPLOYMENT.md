# Railway Deployment

Recommended Railway setup uses two separate services from this repository.

## Services

1. `clinical-rag-agent`
   - Root directory: `clinical-rag-agent`
   - Dockerfile: `clinical-rag-agent/Dockerfile`
   - Railway config: `clinical-rag-agent/railway.toml`
   - Public networking can stay disabled if Open WebUI reaches it through Railway private networking.

2. `open-webui`
   - Root directory: `open-webui`
   - Dockerfile: `open-webui/Dockerfile`
   - Railway config: `open-webui/railway.toml`
   - This is the public UI service.

## Variables

Copy service variables from:

- `clinical-rag-agent/.env.example`
- `open-webui/.env.example`

Use the same secret value for:

- `clinical-rag-agent`: `CLINICAL_RAG_API_KEY`
- `open-webui`: `OPENAI_API_KEYS`

For Railway, set `OPENAI_API_BASE_URLS` in the `open-webui` service to the private URL of the `clinical-rag-agent` service plus `/v1`.

Keep these Open WebUI variables empty on 1 GB Railway deployments:

- `RAG_EMBEDDING_MODEL`
- `RAG_RERANKING_MODEL`
- `AUXILIARY_EMBEDDING_MODEL`

The root `Dockerfile` is an optional single-container demo path and is not recommended for Railway 1 GB deployments.
