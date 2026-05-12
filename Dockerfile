# syntax=docker/dockerfile:1

ARG USE_SLIM=true
ARG USE_OLLAMA=false
ARG USE_CUDA=false
ARG USE_CUDA_VER=cu128
ARG USE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ARG USE_RERANKING_MODEL=""
ARG USE_AUXILIARY_EMBEDDING_MODEL=TaylorAI/bge-micro-v2
ARG BUILD_HASH=dev-build
ARG NODE_BUILD_MEMORY=4096

######## Open WebUI frontend ########
FROM --platform=$BUILDPLATFORM node:22-alpine3.20 AS webui-build
ARG BUILD_HASH
ARG NODE_BUILD_MEMORY

WORKDIR /app

RUN apk add --no-cache git

COPY open-webui/package.json open-webui/package-lock.json ./
RUN npm ci --force

COPY open-webui ./
ENV APP_BUILD_HASH=${BUILD_HASH}
ENV NODE_OPTIONS=--max-old-space-size=${NODE_BUILD_MEMORY}
RUN npm run build

######## Unified runtime ########
FROM python:3.11.14-slim-bookworm AS runtime

ARG USE_SLIM
ARG USE_OLLAMA
ARG USE_CUDA
ARG USE_CUDA_VER
ARG USE_EMBEDDING_MODEL
ARG USE_RERANKING_MODEL
ARG USE_AUXILIARY_EMBEDDING_MODEL
ARG BUILD_HASH

ENV PYTHONUNBUFFERED=1 \
    ENV=prod \
    PORT=8080 \
    HOST=0.0.0.0 \
    DOCKER=true \
    WEBUI_BUILD_VERSION=${BUILD_HASH} \
    USE_OLLAMA_DOCKER=${USE_OLLAMA} \
    USE_CUDA_DOCKER=${USE_CUDA} \
    USE_SLIM_DOCKER=${USE_SLIM} \
    USE_CUDA_DOCKER_VER=${USE_CUDA_VER} \
    USE_EMBEDDING_MODEL_DOCKER=${USE_EMBEDDING_MODEL} \
    USE_RERANKING_MODEL_DOCKER=${USE_RERANKING_MODEL} \
    USE_AUXILIARY_EMBEDDING_MODEL_DOCKER=${USE_AUXILIARY_EMBEDDING_MODEL} \
    RAG_EMBEDDING_MODEL="" \
    RAG_RERANKING_MODEL="" \
    AUXILIARY_EMBEDDING_MODEL="" \
    SENTENCE_TRANSFORMERS_HOME=/app/backend/data/cache/embedding/models \
    HF_HOME=/app/backend/data/cache/embedding/models \
    WHISPER_MODEL=base \
    WHISPER_MODEL_DIR=/app/backend/data/cache/whisper/models \
    TIKTOKEN_ENCODING_NAME=cl100k_base \
    TIKTOKEN_CACHE_DIR=/app/backend/data/cache/tiktoken \
    SCARF_NO_ANALYTICS=true \
    DO_NOT_TRACK=true \
    ANONYMIZED_TELEMETRY=false \
    ENABLE_OPENAI_API=true \
    OPENAI_API_BASE_URLS=http://127.0.0.1:8000/v1 \
    CLINICAL_RAG_DATA_DIR=/app/backend/data/clinical-rag-agent \
    CLINICAL_RAG_LLM_PROVIDER=stub

WORKDIR /app/backend

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      bash curl jq git build-essential pandoc gcc netcat-openbsd \
      libmariadb-dev python3-dev ffmpeg libsm6 libxext6 zstd \
    && rm -rf /var/lib/apt/lists/*

COPY open-webui/backend/requirements.txt ./requirements.txt

ENV UV_LINK_MODE=copy

RUN set -e; \
    pip3 install --no-cache-dir uv; \
    if [ "$USE_CUDA" = "true" ]; then \
      pip3 install 'torch<=2.9.1' torchvision torchaudio --index-url https://download.pytorch.org/whl/$USE_CUDA_DOCKER_VER --no-cache-dir; \
      uv pip install --system -r requirements.txt --no-cache-dir; \
    else \
      pip3 install 'torch<=2.9.1' torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir; \
      uv pip install --system -r requirements.txt --no-cache-dir; \
    fi; \
    if [ "$USE_SLIM" != "true" ]; then \
      if [ -n "$RAG_EMBEDDING_MODEL" ]; then python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL'], device='cpu')"; fi; \
      if [ -n "$AUXILIARY_EMBEDDING_MODEL" ]; then python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['AUXILIARY_EMBEDDING_MODEL'], device='cpu')"; fi; \
      python -c "import os; from faster_whisper import WhisperModel; WhisperModel(os.environ['WHISPER_MODEL'], device='cpu', compute_type='int8', download_root=os.environ['WHISPER_MODEL_DIR'])"; \
      python -c "import os; import tiktoken; tiktoken.get_encoding(os.environ['TIKTOKEN_ENCODING_NAME'])"; \
      python -c "import nltk; nltk.download('punkt_tab')"; \
    fi; \
    mkdir -p /app/backend/data

RUN if [ "$USE_OLLAMA" = "true" ]; then \
      curl -fsSL https://ollama.com/install.sh | sh; \
    fi

COPY --from=webui-build /app/build /app/build
COPY --from=webui-build /app/CHANGELOG.md /app/CHANGELOG.md
COPY --from=webui-build /app/package.json /app/package.json

COPY open-webui/backend ./

COPY clinical-rag-agent /opt/clinical-rag-agent
RUN pip3 install --no-cache-dir "/opt/clinical-rag-agent[dev]"

COPY scripts/start-unified.sh /usr/local/bin/start-unified.sh
RUN chmod +x /usr/local/bin/start-unified.sh

EXPOSE 8080

HEALTHCHECK CMD curl --silent --fail http://localhost:${PORT:-8080}/health | jq -ne 'input.status == true' || exit 1

CMD ["start-unified.sh"]
