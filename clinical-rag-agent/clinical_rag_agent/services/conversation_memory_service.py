from clinical_rag_agent.schemas.clinical import PatientSession


class ConversationMemoryService:
    def recent_context(self, session: PatientSession, turns: int = 4) -> str:
        recent = session.turns[-turns:]
        return "\n".join(f"User: {turn.user_message}\nAssistant: {turn.assistant_message}" for turn in recent)

