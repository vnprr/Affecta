"""Human-in-the-loop supervision.

Lets a human reviewer (e.g. a supervising therapist) act on a case: add notes,
confirm or reject working hypotheses, override the active focus, and adjust goals.
Decisions are persisted on the case state and therefore influence future sessions
(the therapeutic prompt skips human-rejected hypotheses and honors the override
focus).
"""

from datetime import datetime, timezone
from uuid import uuid4

from clinical_rag_agent.schemas.therapy import (
    HumanReviewDecision,
    HumanReviewNote,
    TherapeuticCaseState,
    TherapyGoalStatus,
)
from clinical_rag_agent.services.therapy_state_service import TherapyStateService


class HumanReviewError(ValueError):
    """Raised when a review action references something that does not exist."""


class HumanReviewService:
    def __init__(self, therapy_state_service: TherapyStateService):
        self.therapy_state_service = therapy_state_service

    async def add_note(
        self,
        session_id: str,
        note: str,
        reviewer: str | None = None,
        decision: HumanReviewDecision = "comment",
    ) -> TherapeuticCaseState:
        state = await self.therapy_state_service.get_or_create(session_id)
        state.human_review_notes.append(
            HumanReviewNote(
                id=f"review_{uuid4().hex}",
                created_at=datetime.now(timezone.utc),
                note=note,
                reviewer=reviewer,
                decision=decision,
            )
        )
        return await self.therapy_state_service.save(state)

    async def decide_hypothesis(
        self,
        session_id: str,
        hypothesis_id: str,
        decision: HumanReviewDecision,
    ) -> TherapeuticCaseState:
        state = await self.therapy_state_service.get_or_create(session_id)
        hypothesis = next(
            (item for item in state.working_hypotheses if item.id == hypothesis_id), None
        )
        if hypothesis is None:
            raise HumanReviewError(f"Unknown hypothesis: {hypothesis_id}")
        if decision == "approve":
            hypothesis.status = "confirmed_by_human"
            hypothesis.confidence = "high"
        elif decision == "reject":
            hypothesis.status = "rejected_by_human"
        else:
            raise HumanReviewError("Hypothesis decision must be 'approve' or 'reject'.")
        return await self.therapy_state_service.save(state)

    async def set_active_focus(self, session_id: str, focus: str) -> TherapeuticCaseState:
        state = await self.therapy_state_service.get_or_create(session_id)
        state.human_override_focus = focus
        state.active_focus = focus
        return await self.therapy_state_service.save(state)

    async def update_goal(
        self,
        session_id: str,
        goal_id: str,
        status: TherapyGoalStatus | None = None,
        visibility: str | None = None,
    ) -> TherapeuticCaseState:
        state = await self.therapy_state_service.get_or_create(session_id)
        goal = next((item for item in state.therapy_goals if item.id == goal_id), None)
        if goal is None:
            raise HumanReviewError(f"Unknown goal: {goal_id}")
        if status is not None:
            goal.status = status
        if visibility is not None:
            if visibility not in {"visible", "internal"}:
                raise HumanReviewError("visibility must be 'visible' or 'internal'.")
            goal.visibility = visibility
        return await self.therapy_state_service.save(state)
