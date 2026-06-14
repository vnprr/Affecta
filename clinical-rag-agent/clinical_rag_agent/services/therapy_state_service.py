import json
from pathlib import Path
from clinical_rag_agent.schemas.clinical import NlpContext
from clinical_rag_agent.schemas.therapy import (
    TherapeuticCaseState,
    TherapeuticProcessContext,
    TherapyStateUpdate,
)


class TherapyStateService:
    EMOTION_MARKERS = {
        "lęk": ("lęk", "boję", "przeraż", "panic", "afraid", "scared", "anxious"),
        "smutek": ("smut", "depres", "pust", "sad", "depressed", "empty"),
        "złość": ("złoś", "wściek", "angry", "rage"),
        "wstyd": ("wstyd", "guilt", "shame", "winny"),
        "samotność": ("samot", "lonely", "alone"),
    }
    RELATIONSHIP_MARKERS = (
        "partner",
        "partnerka",
        "partnerem",
        "związek",
        "relacja",
        "opuści",
        "odrzuc",
        "zostawi",
        "porzuci",
        "abandoned",
        "rejected",
        "relationship",
        "left me",
    )

    def __init__(self, therapy_states_dir: Path):
        self.therapy_states_dir = therapy_states_dir
        self.therapy_states_dir.mkdir(parents=True, exist_ok=True)

    async def get_or_create(self, session_id: str) -> TherapeuticCaseState:
        path = self._path(session_id)
        if not path.exists():
            return TherapeuticCaseState(session_id=session_id)
        return TherapeuticCaseState.model_validate_json(path.read_text(encoding="utf-8"))

    async def save(self, state: TherapeuticCaseState) -> TherapeuticCaseState:
        self._path(state.session_id).write_text(
            json.dumps(state.model_dump(), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        return state

    async def update_after_turn(
        self,
        state: TherapeuticCaseState,
        user_message: str,
        assistant_message: str,
        therapy_context: TherapeuticProcessContext,
        nlp_context: NlpContext,
    ) -> TherapeuticCaseState:
        update = self.build_update(user_message, assistant_message, therapy_context, nlp_context)
        await self.apply_update(state, update)
        return await self.save(state)

    async def apply_update(
        self,
        state: TherapeuticCaseState,
        update: TherapyStateUpdate,
    ) -> TherapeuticCaseState:
        state.session_count += 1
        state.current_stage = self._stage_for_count(state.session_count)
        self._extend_unique(state.presenting_problems, update.new_presenting_problems)
        self._extend_unique(state.current_emotional_state, update.new_emotional_states)
        self._extend_unique(state.recurring_patterns, update.new_patterns)
        self._extend_unique(state.relational_patterns, update.new_relational_patterns)
        self._extend_unique(state.cognitive_patterns, update.new_cognitive_patterns)
        self._extend_unique(state.behavioral_patterns, update.new_behavioral_patterns)
        self._extend_hypotheses(state.working_hypotheses, update.new_hypotheses)
        if update.updated_active_focus:
            state.active_focus = update.updated_active_focus
        if update.summary_note:
            state.last_session_summary = update.summary_note
        self._extend_unique(state.open_questions, update.open_questions)
        self._extend_unique(state.suggested_next_steps, update.suggested_next_steps)
        if update.longitudinal_summary_addition:
            state.longitudinal_summary = self._append_summary(
                state.longitudinal_summary,
                update.longitudinal_summary_addition,
            )
        self._trim_state_lists(state)
        return state

    def build_update(
        self,
        user_message: str,
        assistant_message: str,
        therapy_context: TherapeuticProcessContext,
        nlp_context: NlpContext,
    ) -> TherapyStateUpdate:
        lower = user_message.lower()
        emotions = [
            label
            for label, markers in self.EMOTION_MARKERS.items()
            if any(marker in lower for marker in markers)
        ]
        patterns: list[str] = []
        if any(marker in lower for marker in self.RELATIONSHIP_MARKERS):
            patterns.append("relationship pattern")
        if "zawsze" in lower or "always" in lower:
            patterns.append("all-or-nothing recurring framing")
        if "nie wiem czemu" in lower or "why am i like this" in lower:
            patterns.append("self-questioning pattern")

        problems = [entity.label for entity in nlp_context.entities if entity.label in {"sleep", "mood", "treatment"}]
        summary = self._summary_note(user_message, assistant_message, therapy_context)
        return TherapyStateUpdate(
            new_presenting_problems=problems,
            new_emotional_states=emotions,
            new_patterns=patterns,
            new_relational_patterns=patterns if therapy_context.therapeutic_focus == "relationship pattern" else [],
            updated_active_focus=therapy_context.therapeutic_focus,
            summary_note=summary,
            longitudinal_summary_addition=summary,
            open_questions=[therapy_context.question_goal] if therapy_context.question_goal else [],
            suggested_next_steps=[therapy_context.question_goal] if therapy_context.question_goal else [],
        )

    def _path(self, session_id: str) -> Path:
        safe_id = self._safe_session_id(session_id)
        return self.therapy_states_dir / f"{safe_id}.json"

    @staticmethod
    def _safe_session_id(session_id: str) -> str:
        return "".join(char for char in session_id if char.isalnum() or char in {"-", "_"}) or "default"

    @staticmethod
    def _extend_unique(target: list[str], values: list[str]) -> None:
        existing = {item.lower() for item in target}
        for value in values:
            normalized = value.strip()
            if normalized and normalized.lower() not in existing:
                target.append(normalized)
                existing.add(normalized.lower())

    @staticmethod
    def _extend_hypotheses(target, values) -> None:
        existing = {hypothesis.id for hypothesis in target}
        for hypothesis in values:
            if hypothesis.id not in existing:
                target.append(hypothesis)
                existing.add(hypothesis.id)

    @staticmethod
    def _append_summary(existing: str | None, addition: str) -> str:
        normalized = " ".join(addition.split())
        if not normalized:
            return existing or ""
        if not existing:
            return normalized[:1200]
        if normalized.lower() in existing.lower():
            return existing
        combined = f"{existing}\n{normalized}"
        return combined[-2400:]

    @staticmethod
    def _trim_state_lists(state: TherapeuticCaseState, max_items: int = 30) -> None:
        for name in (
            "presenting_problems",
            "current_emotional_state",
            "recurring_patterns",
            "relational_patterns",
            "cognitive_patterns",
            "behavioral_patterns",
            "open_questions",
            "suggested_next_steps",
        ):
            values = getattr(state, name)
            if len(values) > max_items:
                setattr(state, name, values[-max_items:])

    @staticmethod
    def _stage_for_count(session_count: int):
        if session_count <= 1:
            return "intake"
        if session_count <= 4:
            return "early_sessions"
        return "ongoing_work"

    @staticmethod
    def _summary_note(
        user_message: str,
        assistant_message: str,
        therapy_context: TherapeuticProcessContext,
    ) -> str:
        user_excerpt = " ".join(user_message.split())[:240]
        assistant_excerpt = " ".join(assistant_message.split())[:180]
        return (
            f"Mode: {therapy_context.session_mode}. Focus: {therapy_context.therapeutic_focus}. "
            f"User: {user_excerpt}. Assistant: {assistant_excerpt}"
        )
