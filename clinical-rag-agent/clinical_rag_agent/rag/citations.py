from clinical_rag_agent.schemas.rag import DocumentChunk


def format_citations(chunks: list[DocumentChunk]) -> list[str]:
    return [chunk.id for chunk in chunks]


def citation_summary(chunks: list[DocumentChunk]) -> str:
    if not chunks:
        return ""
    return " ".join(f"[{chunk.id}] {chunk.title}" for chunk in chunks)

