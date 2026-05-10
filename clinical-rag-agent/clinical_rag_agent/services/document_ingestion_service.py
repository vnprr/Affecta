from clinical_rag_agent.schemas.rag import DocumentChunk, DocumentInput
from clinical_rag_agent.services.rag_service import RagService


class DocumentIngestionService:
    def __init__(self, rag_service: RagService):
        self.rag_service = rag_service

    async def ingest_documents(self, documents: list[DocumentInput]) -> list[DocumentChunk]:
        return await self.rag_service.ingest(documents)

