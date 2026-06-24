from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from clinical_rag_agent.api.deps import get_container, verify_bearer_token
from clinical_rag_agent.schemas.therapy import HumanReviewDecision, TherapyGoalStatus
from clinical_rag_agent.services.container import AppContainer
from clinical_rag_agent.services.human_review_service import HumanReviewError


router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class HumanReviewNoteRequest(BaseModel):
    note: str
    reviewer: str | None = None
    decision: HumanReviewDecision = "comment"


class HumanDecisionRequest(BaseModel):
    hypothesis_id: str
    decision: HumanReviewDecision


class ActiveFocusRequest(BaseModel):
    focus: str


class GoalUpdateRequest(BaseModel):
    status: TherapyGoalStatus | None = None
    visibility: str | None = None


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


@router.post("/{session_id}/human-review-note")
async def add_human_review_note(
    session_id: str,
    payload: HumanReviewNoteRequest,
    request: Request,
    container: AppContainer = Depends(get_container),
):
    verify_bearer_token(request, container)
    state = await container.human_review_service.add_note(
        session_id, payload.note, payload.reviewer, payload.decision
    )
    return state.model_dump()


@router.post("/{session_id}/human-decision")
async def decide_hypothesis(
    session_id: str,
    payload: HumanDecisionRequest,
    request: Request,
    container: AppContainer = Depends(get_container),
):
    verify_bearer_token(request, container)
    try:
        state = await container.human_review_service.decide_hypothesis(
            session_id, payload.hypothesis_id, payload.decision
        )
    except HumanReviewError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return state.model_dump()


@router.post("/{session_id}/active-focus")
async def set_active_focus(
    session_id: str,
    payload: ActiveFocusRequest,
    request: Request,
    container: AppContainer = Depends(get_container),
):
    verify_bearer_token(request, container)
    state = await container.human_review_service.set_active_focus(session_id, payload.focus)
    return state.model_dump()


@router.patch("/{session_id}/goals/{goal_id}")
async def update_goal(
    session_id: str,
    goal_id: str,
    payload: GoalUpdateRequest,
    request: Request,
    container: AppContainer = Depends(get_container),
):
    verify_bearer_token(request, container)
    try:
        state = await container.human_review_service.update_goal(
            session_id, goal_id, payload.status, payload.visibility
        )
    except HumanReviewError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return state.model_dump()
