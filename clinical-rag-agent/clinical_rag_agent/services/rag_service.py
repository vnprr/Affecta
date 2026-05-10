import json
from pathlib import Path
from clinical_rag_agent.rag.chunking import chunk_documents
from clinical_rag_agent.rag.retriever import LocalRetriever
from clinical_rag_agent.rag.source_quality import classify_source_quality, estimate_source_agreement
from clinical_rag_agent.schemas.rag import DocumentChunk, DocumentInput, RetrievalResult


class RagService:
    def __init__(self, rag_dir: Path, max_chunks: int = 4):
        self.rag_dir = rag_dir
        self.max_chunks = max_chunks
        self.rag_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_path = self.rag_dir / "chunks.jsonl"
        self.retriever = LocalRetriever(self.chunks_path)
        self._seed_if_empty()

    async def ingest(self, documents: list[DocumentInput]) -> list[DocumentChunk]:
        existing = self._load_chunks()
        start = len(existing)
        chunks = []
        for offset, chunk in enumerate(chunk_documents(documents)):
            chunks.append(chunk.model_copy(update={"id": f"{chunk.id}_{start + offset}"}))
        with self.chunks_path.open("a", encoding="utf-8") as handle:
            for chunk in chunks:
                handle.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + "\n")
        return chunks

    async def retrieve(self, query: str, filters: dict[str, str] | None = None) -> RetrievalResult:
        del filters
        chunks = self._load_chunks()
        results = self.retriever.search(query, chunks, limit=self.max_chunks)
        coverage = round(sum(max(chunk.score, 0.0) for chunk in results) / max(len(results), 1), 2)
        return RetrievalResult(
            query=query,
            chunks=results,
            evidence_coverage=min(coverage, 1.0),
            source_agreement=estimate_source_agreement(results),
            clinical_source_quality=classify_source_quality(results),
            missing_evidence=[] if results else ["clinical evidence"],
            conflicting_evidence=[],
        )

    def _load_chunks(self) -> list[DocumentChunk]:
        if not self.chunks_path.exists():
            return []
        chunks: list[DocumentChunk] = []
        for line in self.chunks_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                chunks.append(DocumentChunk.model_validate_json(line))
        return chunks

    def _seed_if_empty(self) -> None:
        if self.chunks_path.exists() and self.chunks_path.stat().st_size > 0:
            return
        seed_docs = [
            DocumentInput(
                source="clinical_safety_basics",
                title="Clinical safety response principles",
                text=(
                    "Mental health support responses should avoid definitive diagnosis from a short conversation. "
                    "They may describe possibilities as hypotheses and should recommend fuller assessment by a qualified clinician. "
                    "If self-harm or suicide risk appears, the response should prioritize immediate safety and urgent local support."
                    "\n\nOdpowiedzi wspierające zdrowie psychiczne nie powinny stawiać pewnej diagnozy po krótkiej rozmowie. "
                    "Mogą opisywać możliwości jako hipotezy i powinny zachęcać do pełniejszej oceny u wykwalifikowanego specjalisty. "
                    "Jeśli pojawia się ryzyko samookaleczenia lub samobójstwa, pierwszeństwo ma natychmiastowe bezpieczeństwo i lokalna pomoc."
                ),
                metadata={"quality": "high"},
            ),
            DocumentInput(
                source="delusion_response_basics",
                title="Responding to distressing fixed beliefs",
                text=(
                    "When a person reports a belief that others are controlling, tracking, or influencing them, a safe response "
                    "acknowledges the fear and distress without confirming the unverified belief. It can invite reality-testing, "
                    "support from trusted people, and professional evaluation."
                    "\n\nGdy osoba mówi, że inni ją śledzą, kontrolują lub sterują jej myślami, bezpieczna odpowiedź uznaje lęk "
                    "i cierpienie bez potwierdzania niezweryfikowanego przekonania. Może zachęcać do oddzielenia uczuć od tego, "
                    "co da się potwierdzić, wsparcia zaufanej osoby i konsultacji specjalistycznej."
                ),
                metadata={"quality": "high"},
            ),
            DocumentInput(
                source="psychoeducation_mood_sleep",
                title="Mood, sleep, and activation psychoeducation",
                text=(
                    "Insomnia, racing thoughts, elevated energy, irritability, and grandiose ideas can be associated with manic "
                    "or hypomanic symptoms, but these observations are not a diagnosis. Low mood, loss of interest, sleep changes, "
                    "and appetite changes can be associated with depressive symptoms and require contextual assessment."
                    "\n\nBezsenność, gonitwa myśli, podwyższona energia, drażliwość i wielkościowe przekonania mogą być związane "
                    "z objawami maniakalnymi lub hipomaniakalnymi, ale same obserwacje nie są diagnozą. Obniżony nastrój, utrata "
                    "zainteresowań, zmiany snu i apetytu mogą wiązać się z objawami depresyjnymi i wymagają oceny kontekstu."
                ),
                metadata={"quality": "medium"},
            ),
            DocumentInput(
                source="treatment_scope_basics",
                title="Treatment planning boundaries",
                text=(
                    "A general support system can provide psychoeducation, encourage tracking symptoms, and suggest discussing "
                    "care options with a licensed professional. It should not prescribe medication, create a definitive treatment "
                    "plan, or replace clinical care."
                    "\n\nOgólny system wsparcia może oferować psychoedukację, zachęcać do obserwacji objawów i sugerować omówienie "
                    "możliwości pomocy z uprawnionym specjalistą. Nie powinien przepisywać leków, tworzyć definitywnego planu leczenia "
                    "ani zastępować opieki klinicznej."
                ),
                metadata={"quality": "high"},
            ),
        ]
        chunks = chunk_documents(seed_docs)
        self.chunks_path.write_text(
            "\n".join(json.dumps(chunk.model_dump(), ensure_ascii=False) for chunk in chunks) + "\n",
            encoding="utf-8",
        )
