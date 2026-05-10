from clinical_rag_agent.schemas.rag import DocumentChunk


class RerankingService:
    def rerank(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        return sorted(chunks, key=lambda chunk: chunk.score, reverse=True)

