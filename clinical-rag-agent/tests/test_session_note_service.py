from datetime import datetime, timezone

import pytest

from clinical_rag_agent.schemas.therapy import SessionNote
from clinical_rag_agent.services.session_note_service import SessionNoteService


def _note(session_id: str, summary: str) -> SessionNote:
    return SessionNote(
        id=f"note-{summary}",
        session_id=session_id,
        created_at=datetime.now(timezone.utc),
        user_message_excerpt="user excerpt",
        assistant_response_excerpt="assistant excerpt",
        summary=summary,
    )


@pytest.mark.asyncio
async def test_session_note_service_appends_lists_and_gets_latest(tmp_path):
    service = SessionNoteService(tmp_path / "session_notes")

    await service.append_note(_note("s1", "first"))
    await service.append_note(_note("s1", "second"))

    notes = await service.list_notes("s1")
    latest = await service.latest_note("s1")

    assert [note.summary for note in notes] == ["first", "second"]
    assert latest is not None
    assert latest.summary == "second"


@pytest.mark.asyncio
async def test_session_note_service_sanitizes_session_id(tmp_path):
    service = SessionNoteService(tmp_path / "session_notes")

    await service.append_note(_note("session/with spaces", "safe"))

    assert (tmp_path / "session_notes" / "sessionwithspaces.jsonl").exists()
    assert (await service.latest_note("session/with spaces")).summary == "safe"
