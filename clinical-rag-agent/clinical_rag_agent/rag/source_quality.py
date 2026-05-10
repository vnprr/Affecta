from clinical_rag_agent.schemas.rag import DocumentChunk


def classify_source_quality(chunks: list[DocumentChunk]) -> str:
    if not chunks:
        return "missing"
    if any(chunk.metadata.get("quality") == "high" for chunk in chunks):
        return "high"
    if any(chunk.metadata.get("quality") == "medium" for chunk in chunks):
        return "medium"
    return "low"


def estimate_source_agreement(chunks: list[DocumentChunk]) -> float:
    if not chunks:
        return 0.0
    sources = {chunk.source for chunk in chunks}
    return round(min(1.0, 0.55 + (len(sources) - 1) * 0.15), 2)

