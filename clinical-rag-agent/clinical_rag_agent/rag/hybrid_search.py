import math
from collections import Counter
from clinical_rag_agent.rag.embeddings import HashEmbeddingModel, cosine_similarity, tokenize
from clinical_rag_agent.schemas.rag import DocumentChunk


class HybridRetriever:
    def __init__(self, embedding_model: HashEmbeddingModel | None = None):
        self.embedding_model = embedding_model or HashEmbeddingModel()

    def search(self, query: str, chunks: list[DocumentChunk], limit: int = 4) -> list[DocumentChunk]:
        if not chunks:
            return []
        query_tokens = tokenize(query)
        query_embedding = self.embedding_model.embed(query)
        doc_tokens = [tokenize(chunk.text) for chunk in chunks]
        doc_freq: Counter[str] = Counter()
        for tokens in doc_tokens:
            doc_freq.update(set(tokens))

        scored: list[DocumentChunk] = []
        for chunk, tokens in zip(chunks, doc_tokens, strict=True):
            lexical = self._bm25(query_tokens, tokens, doc_tokens, doc_freq)
            semantic = cosine_similarity(query_embedding, self.embedding_model.embed(chunk.text))
            combined = (0.65 * lexical) + (0.35 * max(semantic, 0.0))
            scored.append(chunk.model_copy(update={"score": round(combined, 4)}))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit]

    def _bm25(
        self,
        query_tokens: list[str],
        tokens: list[str],
        all_doc_tokens: list[list[str]],
        doc_freq: Counter[str],
    ) -> float:
        if not query_tokens or not tokens:
            return 0.0
        term_counts = Counter(tokens)
        avg_doc_len = sum(len(doc) for doc in all_doc_tokens) / max(len(all_doc_tokens), 1)
        k1 = 1.5
        b = 0.75
        score = 0.0
        for token in query_tokens:
            tf = term_counts[token]
            if tf == 0:
                continue
            df = doc_freq[token]
            idf = math.log(1 + (len(all_doc_tokens) - df + 0.5) / (df + 0.5))
            denom = tf + k1 * (1 - b + b * len(tokens) / max(avg_doc_len, 1))
            score += idf * (tf * (k1 + 1)) / denom
        return min(score / max(len(set(query_tokens)), 1), 1.0)

