from fastapi.testclient import TestClient
from clinical_rag_agent.config import get_settings

AUTH = {"Authorization": "Bearer local-dev-key"}


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("CLINICAL_RAG_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("CLINICAL_RAG_LLM_PROVIDER", "stub")
    get_settings.cache_clear()
    from clinical_rag_agent.main import create_app

    return TestClient(create_app())


def _seed_session(client: TestClient, session_id: str) -> None:
    client.post(
        "/v1/chat/completions",
        headers=AUTH,
        json={
            "model": "clinical-rag-agent",
            "messages": [
                {"role": "user", "content": "I am scared she will leave me and I keep checking my phone."}
            ],
            "stream": False,
            "metadata": {"session_id": session_id},
        },
    )


def test_reviewer_can_reject_hypothesis_and_set_focus(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    session_id = "review-api"
    _seed_session(client, session_id)

    state = client.get(f"/api/sessions/{session_id}/therapy-state", headers=AUTH).json()
    hypothesis_id = state["working_hypotheses"][0]["id"]

    reject = client.post(
        f"/api/sessions/{session_id}/human-decision",
        headers=AUTH,
        json={"hypothesis_id": hypothesis_id, "decision": "reject"},
    )
    assert reject.status_code == 200
    rejected = next(h for h in reject.json()["working_hypotheses"] if h["id"] == hypothesis_id)
    assert rejected["status"] == "rejected_by_human"

    focus = client.post(
        f"/api/sessions/{session_id}/active-focus",
        headers=AUTH,
        json={"focus": "self-worth"},
    )
    assert focus.status_code == 200
    assert focus.json()["human_override_focus"] == "self-worth"
    assert focus.json()["active_focus"] == "self-worth"


def test_reviewer_note_and_unknown_hypothesis(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    session_id = "review-api-2"
    _seed_session(client, session_id)

    note = client.post(
        f"/api/sessions/{session_id}/human-review-note",
        headers=AUTH,
        json={"note": "Watch relational triggers next session.", "reviewer": "dr.smith", "decision": "needs_attention"},
    )
    assert note.status_code == 200
    assert note.json()["human_review_notes"][0]["reviewer"] == "dr.smith"

    bad = client.post(
        f"/api/sessions/{session_id}/human-decision",
        headers=AUTH,
        json={"hypothesis_id": "does-not-exist", "decision": "approve"},
    )
    assert bad.status_code == 400
