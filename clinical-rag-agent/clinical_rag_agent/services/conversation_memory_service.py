from clinical_rag_agent.schemas.clinical import PatientSession
from clinical_rag_agent.schemas.therapy import TherapeuticCaseState


class ConversationMemoryService:
    def recent_context(self, session: PatientSession, turns: int = 4) -> str:
        recent = session.turns[-turns:]
        return "\n".join(f"User: {turn.user_message}\nAssistant: {turn.assistant_message}" for turn in recent)

    def build_longitudinal_summary(self, session: PatientSession, therapy_state: TherapeuticCaseState) -> str:
        parts: list[str] = []
        if therapy_state.longitudinal_summary:
            parts.append(therapy_state.longitudinal_summary)
        if therapy_state.last_session_summary:
            parts.append(f"Last session: {therapy_state.last_session_summary}")
        if therapy_state.active_focus:
            parts.append(f"Active focus: {therapy_state.active_focus}")
        if therapy_state.recurring_patterns:
            parts.append(f"Recurring patterns: {', '.join(therapy_state.recurring_patterns[:6])}")
        if therapy_state.therapy_goals:
            goals = [
                f"{goal.title} ({goal.status})"
                for goal in therapy_state.therapy_goals
                if goal.status == "active"
            ]
            if goals:
                parts.append(f"Active goals: {', '.join(goals[:4])}")
        if not parts and session.turns:
            parts.append("This is an early therapeutic conversation with limited longitudinal material.")
        return "\n".join(parts)

    def extract_visible_context(self, session: PatientSession, therapy_state: TherapeuticCaseState) -> str:
        sections: list[str] = []
        recent = self.recent_context(session)
        if recent:
            sections.append(f"Recent conversation:\n{recent}")
        sections.append(f"Current stage: {therapy_state.current_stage}")
        if therapy_state.active_focus:
            sections.append(f"Active focus: {therapy_state.active_focus}")
        if therapy_state.current_emotional_state:
            sections.append(f"Current emotional themes: {', '.join(therapy_state.current_emotional_state[:6])}")
        if therapy_state.recurring_patterns:
            sections.append(f"Recurring patterns: {', '.join(therapy_state.recurring_patterns[:6])}")
        if therapy_state.working_hypotheses:
            hypotheses = [
                f"{hypothesis.label} ({hypothesis.confidence})"
                for hypothesis in therapy_state.working_hypotheses
                if hypothesis.status not in {"rejected_by_human", "weakened"}
            ]
            if hypotheses:
                sections.append(f"Working hypotheses for internal guidance only: {', '.join(hypotheses[:4])}")
        if therapy_state.therapy_goals:
            goals = [f"{goal.title} ({goal.status})" for goal in therapy_state.therapy_goals]
            sections.append(f"Therapy goals: {', '.join(goals[:4])}")
        return "\n\n".join(sections)
