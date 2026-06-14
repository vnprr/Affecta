from fastapi import APIRouter, Depends, Request
from clinical_rag_agent.api.deps import get_container, verify_bearer_token
from clinical_rag_agent.services.container import AppContainer


router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("")
async def list_sessions(request: Request, container: AppContainer = Depends(get_container)):
    verify_bearer_token(request, container)
    return {"sessions": await container.session_service.list_sessions()}


@router.get("/{session_id}/notes")
async def list_session_notes(session_id: str, request: Request, container: AppContainer = Depends(get_container)):
    verify_bearer_token(request, container)
    notes = await container.session_note_service.list_notes(session_id)
    return {"notes": [note.model_dump() for note in notes]}


@router.get("/{session_id}/therapy-state")
async def get_therapy_state(session_id: str, request: Request, container: AppContainer = Depends(get_container)):
    verify_bearer_token(request, container)
    state = await container.therapy_state_service.get_or_create(session_id)
    return state.model_dump()


@router.get("/{session_id}")
async def get_session(session_id: str, request: Request, container: AppContainer = Depends(get_container)):
    verify_bearer_token(request, container)
    session = await container.session_service.get_session(session_id)
    return session.model_dump()
