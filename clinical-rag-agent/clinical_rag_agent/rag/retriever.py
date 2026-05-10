from pathlib import Path
from clinical_rag_agent.rag.hybrid_search import HybridRetriever
from clinical_rag_agent.schemas.rag import DocumentChunk


class LocalRetriever:
    def __init__(self, storage_path: Path, retriever: HybridRetriever | None = None):
        self.storage_path = storage_path
        self.retriever = retriever or HybridRetriever()

    def search(self, query: str, chunks: list[DocumentChunk], limit: int = 4) -> list[DocumentChunk]:
        return self.retriever.search(query, chunks, limit=limit)

