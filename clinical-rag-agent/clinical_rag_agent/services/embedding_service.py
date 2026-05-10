from clinical_rag_agent.rag.embeddings import HashEmbeddingModel


class EmbeddingService:
    def __init__(self):
        self.model = HashEmbeddingModel()

    def embed(self, text: str) -> list[float]:
        return self.model.embed(text)

