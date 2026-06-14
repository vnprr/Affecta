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


def test_openai_models_endpoint(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    response = client.get("/v1/models", headers={"Authorization": "Bearer local-dev-key"})

    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "clinical-rag-agent"


def test_openai_chat_completion_non_stream(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer local-dev-key"},
        json={
            "model": "clinical-rag-agent",
            "messages": [{"role": "user", "content": "Mam bezsenność i gonitwę myśli."}],
            "stream": False,
            "metadata": {"session_id": "test-session"},
        },
    )

    assert response.status_code == 200
    content = response.json()["choices"][0]["message"]["content"]
    assert "opowiedzieć" in content.lower() or "co" in content.lower()
    therapy_state_path = tmp_path / "therapy_states" / "test-session.json"
    session_notes_path = tmp_path / "session_notes" / "test-session.jsonl"
    session_path = tmp_path / "sessions" / "test-session.json"
    assert therapy_state_path.exists()
    assert session_notes_path.exists()
    session_payload = json.loads(session_path.read_text(encoding="utf-8"))
    turn_metadata = session_payload["turns"][-1]["metadata"]
    assert turn_metadata["therapy"]["session_note_id"].startswith("note_")

    notes_response = client.get(
        "/api/sessions/test-session/notes",
        headers={"Authorization": "Bearer local-dev-key"},
    )
    state_response = client.get(
        "/api/sessions/test-session/therapy-state",
        headers={"Authorization": "Bearer local-dev-key"},
    )
    assert notes_response.status_code == 200
    assert notes_response.json()["notes"][0]["id"] == turn_metadata["therapy"]["session_note_id"]
    assert state_response.status_code == 200
    assert state_response.json()["session_count"] == 1


def test_openai_chat_completion_stream(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    with client.stream(
        "POST",
        "/v1/chat/completions",
        headers={"Authorization": "Bearer local-dev-key"},
        json={
            "model": "clinical-rag-agent",
            "messages": [{"role": "user", "content": "Czy to może być depresja?"}],
            "stream": True,
            "metadata": {"session_id": "test-stream"},
        },
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert "data: [DONE]" in body
