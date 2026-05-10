from fastapi.testclient import TestClient
from clinical_rag_agent.config import get_settings
from clinical_rag_agent.main import create_app


def test_openai_models_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv("CLINICAL_RAG_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/v1/models", headers={"Authorization": "Bearer local-dev-key"})

    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "clinical-rag-agent"


def test_openai_chat_completion_non_stream(monkeypatch, tmp_path):
    monkeypatch.setenv("CLINICAL_RAG_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    client = TestClient(create_app())

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
    assert "diagno" in content.lower()


def test_openai_chat_completion_stream(monkeypatch, tmp_path):
    monkeypatch.setenv("CLINICAL_RAG_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    client = TestClient(create_app())

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

