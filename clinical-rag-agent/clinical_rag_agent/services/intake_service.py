"""Intake reasoning for the first sessions.

During the ``intake`` stage this service makes sure the case state captures why the
user came: presenting problems, an initial direction, and which context is still
missing. It is deliberately light and rule-based; the visible intake conversation
is handled by the main therapeutic prompt. It never diagnoses.
"""

from clinical_rag_agent.schemas.clinical import NlpContext
from clinical_rag_agent.schemas.therapy import TherapeuticCaseState


class IntakeService:
    # Context dimensions a useful intake should eventually cover.
    CONTEXT_CHECKS: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("duration / when it started", ("started", "since", "od kiedy", "zaczęło", "zaczelo")),
        ("sleep", ("sleep", "insomnia", "sen", "śpię", "spie", "bezsenn")),
        ("relationships / support", ("partner", "friend", "family", "relacj", "przyjaci", "rodzin")),
        ("daily functioning / work", ("work", "job", "study", "praca", "studia", "szkoł", "szkol")),
        ("safety", ("safe", "harm", "suicid", "bezpiecz", "krzywd")),
    )

    def enrich(
        self,
        state: TherapeuticCaseState,
        user_message: str,
        nlp_context: NlpContext | None = None,
    ) -> TherapeuticCaseState:
        if state.current_stage != "intake":
            return state

        lower = user_message.lower()
        covered_history = (state.longitudinal_summary or "").lower() + " " + lower
        missing = [
            label
            for label, markers in self.CONTEXT_CHECKS
            if not any(marker in covered_history for marker in markers)
        ]
        state.missing_context = missing

        if not state.presenting_problems:
            self._seed_presenting_problem(state, user_message, nlp_context)

        # Intake is considered complete once we have a presenting problem and most
        # of the core context has been touched.
        state.intake_complete = bool(state.presenting_problems) and len(missing) <= 1
        return state

    def _seed_presenting_problem(
        self,
        state: TherapeuticCaseState,
        user_message: str,
        nlp_context: NlpContext | None,
    ) -> None:
        if nlp_context is not None and nlp_context.entities:
            labels = [
                entity.label
                for entity in nlp_context.entities
                if entity.label in {"sleep", "mood", "treatment", "relationship"}
            ]
            if labels:
                state.presenting_problems.extend(dict.fromkeys(labels))
                return
        excerpt = " ".join(user_message.split())[:160]
        if excerpt:
            state.presenting_problems.append(f"initial concern: {excerpt}")
