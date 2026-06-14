from clinical_rag_agent.schemas.clinical import NlpContext, PatientSession
from clinical_rag_agent.schemas.therapy import TherapeuticCaseState, TherapeuticProcessContext


class TherapeuticProcessService:
    STRONG_DISTRESS_WORDS = (
        "nie daję rady",
        "panika",
        "panic",
        "przeraż",
        "rozpacz",
        "załam",
        "can't cope",
        "overwhelmed",
        "terrified",
    )
    RELATIONSHIP_WORDS = (
        "she",
        "he",
        "partner",
        "partnerka",
        "partnerem",
        "left",
        "abandoned",
        "rejected",
        "relationship",
        "związek",
        "relacja",
        "opuści",
        "odrzuc",
        "porzuci",
        "zostawi",
    )
    WHY_WORDS = (
        "why am i like this",
        "why do i",
        "czemu taki jestem",
        "czemu taka jestem",
        "dlaczego taki jestem",
        "dlaczego taka jestem",
        "dlaczego tak mam",
    )
    EXPLANATION_WORDS = (
        "explain",
        "why does",
        "what is",
        "wyjaśnij",
        "wytłumacz",
        "dlaczego",
        "co to jest",
        "skąd się bierze",
    )

    async def analyze(
        self,
        user_message: str,
        session: PatientSession,
        therapy_state: TherapeuticCaseState,
        nlp_context: NlpContext,
    ) -> TherapeuticProcessContext:
        del nlp_context
        lower = user_message.lower()

        if any(word in lower for word in self.STRONG_DISTRESS_WORDS):
            if any(word in lower for word in ("panika", "panic", "przeraż", "terrified")):
                return self._context(
                    "stabilization",
                    "immediate emotional stabilization",
                    "validate emotion and ask one grounding question",
                    True,
                    "identify what would help the user feel slightly safer in this moment",
                )
            return self._context(
                "support",
                "current emotional distress",
                "validate emotion and ask one grounding question",
                True,
                "understand what feels most difficult right now",
            )

        if any(word in lower for word in self.RELATIONSHIP_WORDS):
            return self._context(
                "pattern_reflection",
                "relationship pattern",
                "reflect recurring relationship pattern gently",
                True,
                "explore what this relationship moment brought up emotionally",
            )

        if any(word in lower for word in self.WHY_WORDS):
            return self._context(
                "exploration",
                therapy_state.active_focus or "self-understanding",
                "summarize and ask what feels most important now",
                True,
                "explore the meaning behind the user's self-question",
            )

        if any(word in lower for word in self.EXPLANATION_WORDS):
            return self._context(
                "psychoeducation",
                therapy_state.active_focus or "psychoeducation connected to lived experience",
                "provide brief psychoeducation and return to the user's experience",
                True,
                "connect the explanation to the user's own situation",
                should_use_rag=True,
            )

        if len(session.turns) < 2 or therapy_state.session_count == 0:
            return self._context(
                "intake",
                therapy_state.active_focus or "getting to know the user's current concern",
                "summarize and ask what feels most important now",
                True,
                "understand what brought the user here now",
            )

        return self._context(
            "exploration",
            therapy_state.active_focus or "ongoing therapeutic exploration",
            "summarize and ask what feels most important now",
            True,
            "deepen the user's understanding of the current experience",
        )

    @staticmethod
    def _context(
        session_mode,
        therapeutic_focus: str,
        response_strategy: str,
        should_ask_question: bool,
        question_goal: str | None,
        should_use_rag: bool = False,
    ) -> TherapeuticProcessContext:
        return TherapeuticProcessContext(
            session_mode=session_mode,
            therapeutic_focus=therapeutic_focus,
            response_strategy=response_strategy,
            should_ask_question=should_ask_question,
            question_goal=question_goal,
            should_use_rag=should_use_rag,
        )
