from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request
from clinical_rag_agent.api.deps import get_container, verify_bearer_token
from clinical_rag_agent.schemas.rag import DocumentInput
from clinical_rag_agent.services.container import AppContainer


class IngestRequest(BaseModel):
    documents: list[DocumentInput]


router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("")
async def ingest(
    request: Request,
    payload: IngestRequest,
    container: AppContainer = Depends(get_container),
):
    verify_bearer_token(request, container)
    chunks = await container.document_ingestion_service.ingest_documents(payload.documents)
    container.monitoring_service.increment("ingest.documents")
    return {"ingested_chunks": len(chunks), "chunk_ids": [chunk.id for chunk in chunks]}

