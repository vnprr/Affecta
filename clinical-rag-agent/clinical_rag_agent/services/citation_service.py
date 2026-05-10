from clinical_rag_agent.rag.citations import citation_summary, format_citations
from clinical_rag_agent.schemas.rag import DocumentChunk


class CitationService:
    def citations_for_chunks(self, chunks: list[DocumentChunk]) -> list[str]:
        return format_citations(chunks)

    def summary_for_chunks(self, chunks: list[DocumentChunk]) -> str:
        return citation_summary(chunks)

