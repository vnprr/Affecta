from pathlib import Path
from clinical_rag_agent.schemas.clinical import ConversationTurn, PatientSession
from clinical_rag_agent.services.storage_utils import write_json_atomic


class SessionService:
    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    async def get_session(self, session_id: str) -> PatientSession:
        path = self._path(session_id)
        if not path.exists():
            return PatientSession(session_id=session_id)
        return PatientSession.model_validate_json(path.read_text(encoding="utf-8"))

    async def save_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        metadata: dict,
    ) -> PatientSession:
        session = await self.get_session(session_id)
        session.turns.append(
            ConversationTurn(
                user_message=user_message,
                assistant_message=assistant_message,
                metadata=metadata,
            )
        )
        write_json_atomic(self._path(session_id), session.model_dump())
        return session

    async def list_sessions(self) -> list[str]:
        return sorted(path.stem for path in self.sessions_dir.glob("*.json"))

    def _path(self, session_id: str) -> Path:
        safe_id = "".join(char for char in session_id if char.isalnum() or char in {"-", "_"}) or "default"
        return self.sessions_dir / f"{safe_id}.json"
