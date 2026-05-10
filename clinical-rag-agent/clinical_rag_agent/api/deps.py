from fastapi import HTTPException, Request, status
from clinical_rag_agent.services.container import AppContainer


def get_container(request: Request) -> AppContainer:
    return request.app.state.container


def verify_bearer_token(request: Request, container: AppContainer) -> None:
    expected = container.settings.api_key
    if not expected:
        return
    authorization = request.headers.get("authorization", "")
    if authorization == f"Bearer {expected}":
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

