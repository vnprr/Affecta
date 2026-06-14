import json
from pathlib import Path

from clinical_rag_agent.schemas.therapy import SessionNote


class SessionNoteService:
    def __init__(self, base_dir: Path | str = "data/session_notes"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def append_note(self, note: SessionNote) -> None:
        path = self._path(note.session_id)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(note.model_dump(), ensure_ascii=False, default=str))
            handle.write("\n")

    async def list_notes(self, session_id: str) -> list[SessionNote]:
        path = self._path(session_id)
        if not path.exists():
            return []
        notes: list[SessionNote] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                notes.append(SessionNote.model_validate_json(line))
        return notes

    async def latest_note(self, session_id: str) -> SessionNote | None:
        notes = await self.list_notes(session_id)
        return notes[-1] if notes else None

    def _path(self, session_id: str) -> Path:
        safe_id = self._safe_session_id(session_id)
        return self.base_dir / f"{safe_id}.jsonl"

    @staticmethod
    def _safe_session_id(session_id: str) -> str:
        return "".join(char for char in session_id if char.isalnum() or char in {"-", "_"}) or "default"
