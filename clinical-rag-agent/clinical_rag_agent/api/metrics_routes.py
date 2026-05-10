from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from clinical_rag_agent.api.deps import get_container
from clinical_rag_agent.services.container import AppContainer


router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics(container: AppContainer = Depends(get_container)):
    return PlainTextResponse(container.monitoring_service.render_prometheus())

