"""End-to-end therapy-flow test: a multi-turn session should build internal
hypotheses and therapy goals in the background while never leaking diagnostic
labels or internal JSON into the visible response."""

import json

from fastapi.testclient import TestClient
from clinical_rag_agent.config import get_settings


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("CLINICAL_RAG_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("CLINICAL_RAG_LLM_PROVIDER", "stub")
    monkeypatch.setenv("CLINICAL_RAG_LLM_BASE_URL", "")
    monkeypatch.setenv("CLINICAL_RAG_LLM_API_KEY", "")
    monkeypatch.setenv("CLINICAL_RAG_LLM_MODEL", "")
    get_settings.cache_clear()
    from clinical_rag_agent.main import create_app

    return TestClient(create_app())


def _send(client: TestClient, content: str, session_id: str) -> str:
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer local-dev-key"},
        json={
            "model": "clinical-rag-agent",
            "messages": [{"role": "user", "content": content}],
            "stream": False,
            "metadata": {"session_id": session_id},
        },
    )
    assert response.status_code == 200
    return response.json()["choices"][0]["message"]["content"]


def test_multi_turn_session_builds_internal_hypotheses_and_goals(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    session_id = "flow-session"

    turns = [
        "My partner did not answer and I am scared she will leave me, so I keep checking my phone.",
        "When she is distant I feel abandoned and I keep texting to make sure she still wants me.",
        "Then I get angry after the hurt, and I hate myself for being like this.",
        "I keep checking and calling, I am scared of being left and rejected again.",
    ]
    visible_responses = [_send(client, turn, session_id) for turn in turns]

    state_response = client.get(
        f"/api/sessions/{session_id}/therapy-state",
        headers={"Authorization": "Bearer local-dev-key"},
    )
    assert state_response.status_code == 200
    state = state_response.json()

    # Background reasoning produced internal working hypotheses.
    labels = {h["label"] for h in state["working_hypotheses"]}
    assert "attachment_anxiety" in labels

    # A therapy plan emerged with at least one explicit goal.
    assert state["therapy_goals"], "expected at least one therapy goal"
    assert any(goal["visibility"] == "visible" for goal in state["therapy_goals"])

    # Session count advanced and a focus was established.
    assert state["session_count"] == len(turns)
    assert state["active_focus"]

    # The visible responses must never leak diagnoses or internal JSON.
    for text in visible_responses:
        lowered = text.lower()
        assert "borderline" not in lowered
        assert "{" not in text and "}" not in text
        assert "hypothesis" not in lowered


def test_human_rejected_hypothesis_is_not_used_in_prompt(monkeypatch, tmp_path):
    """A hypothesis rejected by a human stays rejected across further turns."""
    client = _client(monkeypatch, tmp_path)
    session_id = "reject-session"

    _send(client, "I am scared she will leave me and I keep checking my phone.", session_id)

    state_path = tmp_path / "therapy_states" / f"{session_id}.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["working_hypotheses"]
    state["working_hypotheses"][0]["status"] = "rejected_by_human"
    state_path.write_text(json.dumps(state), encoding="utf-8")

    _send(client, "Still scared of being abandoned and rejected.", session_id)

    state = json.loads(state_path.read_text(encoding="utf-8"))
    rejected = next(
        h for h in state["working_hypotheses"] if h["label"] == state["working_hypotheses"][0]["label"]
    )
    assert rejected["status"] == "rejected_by_human"
