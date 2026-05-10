import json
import time
from collections.abc import AsyncIterator
from uuid import uuid4
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from clinical_rag_agent.api.deps import get_container, verify_bearer_token
from clinical_rag_agent.schemas.chat import ChatCompletionRequest
from clinical_rag_agent.services.container import AppContainer


router = APIRouter(prefix="/v1", tags=["openai-compatible"])


@router.get("/models")
async def list_models(request: Request, container: AppContainer = Depends(get_container)):
    verify_bearer_token(request, container)
    now = int(time.time())
    return {
        "object": "list",
        "data": [
            {
                "id": container.settings.model_id,
                "object": "model",
                "created": now,
                "owned_by": "clinical-rag-agent",
            }
        ],
    }


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    form_data: ChatCompletionRequest,
    container: AppContainer = Depends(get_container),
):
    verify_bearer_token(request, container)
    user_message = _latest_user_message(form_data)
    session_id = _session_id(form_data, request)
    result = await container.orchestrator.handle_clinical_chat(user_message=user_message, session_id=session_id)
    if form_data.stream:
        return StreamingResponse(
            _stream_openai_chunks(result.text, form_data.model),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    return JSONResponse(_completion_payload(result.text, form_data.model))


def _latest_user_message(form_data: ChatCompletionRequest) -> str:
    for message in reversed(form_data.messages):
        if message.role == "user":
            return message.text_content()
    return form_data.messages[-1].text_content() if form_data.messages else ""


def _session_id(form_data: ChatCompletionRequest, request: Request) -> str:
    metadata = form_data.metadata or {}
    return (
        str(metadata.get("session_id") or metadata.get("chat_id") or metadata.get("conversation_id") or "")
        or request.headers.get("x-session-id")
        or "default"
    )


def _completion_payload(text: str, model: str) -> dict:
    return {
        "id": f"chatcmpl-{uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": len(text.split()),
            "total_tokens": len(text.split()),
        },
    }


async def _stream_openai_chunks(text: str, model: str) -> AsyncIterator[str]:
    completion_id = f"chatcmpl-{uuid4().hex}"
    created = int(time.time())
    role_payload = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
    }
    yield f"data: {json.dumps(role_payload, ensure_ascii=False)}\n\n"
    for token in text.split(" "):
        payload = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": {"content": token + " "}, "finish_reason": None}],
        }
        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    done_payload = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"

