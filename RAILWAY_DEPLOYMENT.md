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

For local Docker Compose, copy service variables from:

- `clinical-rag-agent/.env.example`
- `open-webui/.env.example`

For Railway, copy service variables from:

- `clinical-rag-agent/.env.railway.example`
- `open-webui/.env.railway.example`

Use the same secret value for:

- `clinical-rag-agent`: `CLINICAL_RAG_API_KEY`
- `open-webui`: `OPENAI_API_KEYS`

For Railway, `OPENAI_API_BASE_URLS` in the `open-webui` service must use Railway private networking:

```env
OPENAI_API_BASE_URLS=http://clinical-rag-agent.railway.internal:8000/v1
```

If the Railway service is not named exactly `clinical-rag-agent`, replace the hostname with the real service name:

```env
OPENAI_API_BASE_URLS=http://YOUR_SERVICE_NAME.railway.internal:8000/v1
```

Keep this as `http`, not `https`; it is private service-to-service traffic inside Railway.

Open WebUI stores OpenAI connection settings in its database. If the provider still does not appear after a redeploy, update the same URL manually in `Admin Panel -> Settings -> Connections -> OpenAI API`.

For OpenRouter-backed generation, set these variables in the `clinical-rag-agent` service:

```env
CLINICAL_RAG_LLM_PROVIDER=openai_compatible
CLINICAL_RAG_LLM_BASE_URL=https://openrouter.ai/api/v1
CLINICAL_RAG_LLM_MODEL=google/gemma-4-31b-it:free
CLINICAL_RAG_LLM_API_KEY=<NEW_OPENROUTER_KEY>
```

Keep these Open WebUI variables empty on 1 GB Railway deployments:

- `RAG_EMBEDDING_MODEL`
- `RAG_RERANKING_MODEL`
- `AUXILIARY_EMBEDDING_MODEL`

The root `Dockerfile` is an optional single-container demo path and is not recommended for Railway 1 GB deployments.
