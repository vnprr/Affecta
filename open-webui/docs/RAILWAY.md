# Railway Deployment

This project deploys on Railway from the root `Dockerfile`; Docker Compose is not required.

## Railway settings

Railway should detect `railway.toml` automatically and use:

- Builder: `DOCKERFILE`
- Dockerfile path: `Dockerfile`
- Healthcheck path: `/health`

If Railway asks for a root directory, set it to the directory that contains this file and `Dockerfile`.

## Required variables

Set a stable secret in Railway variables:

```text
WEBUI_SECRET_KEY=<long-random-secret>
```

Without it, Open WebUI generates a temporary secret inside the container. That works for booting, but sessions can be invalidated after redeploys.

## Model provider

For OpenAI-compatible APIs, set these Railway variables:

```text
OPENAI_API_KEY=<your-api-key>
OPENAI_API_BASE_URL=<optional-custom-base-url>
```

For an external Ollama instance, set:

```text
OLLAMA_BASE_URL=https://your-ollama-host
```

If you really want Ollama inside the same Railway container, add this Railway variable before building:

```text
USE_OLLAMA=true
```

The existing Dockerfile declares `ARG USE_OLLAMA`, so Railway can pass that variable during the Docker build. This makes the image larger and still does not pre-pull any Ollama models.

## Persistence

Attach a Railway volume at:

```text
/app/backend/data
```

This keeps uploads, the SQLite database, cache, and Open WebUI data across redeploys.
