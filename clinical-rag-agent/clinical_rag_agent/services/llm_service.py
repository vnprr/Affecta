import httpx
from clinical_rag_agent.config import Settings
from clinical_rag_agent.rag.citations import format_citations
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import NlpContext, PatientSession
from clinical_rag_agent.schemas.rag import GraphContext, RetrievalResult


class LLMService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate_clinical_response(
        self,
        user_message: str,
        session: PatientSession,
        nlp_context: NlpContext,
        rag_context: RetrievalResult,
        graph_context: GraphContext,
    ) -> ChatDraft:
        if self.settings.llm_provider == "openai_compatible" and self.settings.llm_base_url:
            return await self._openai_compatible(user_message, session, nlp_context, rag_context, graph_context)
        return self._stub_response(user_message, nlp_context, rag_context)

    async def _openai_compatible(
        self,
        user_message: str,
        session: PatientSession,
        nlp_context: NlpContext,
        rag_context: RetrievalResult,
        graph_context: GraphContext,
    ) -> ChatDraft:
        evidence = "\n\n".join(f"[{chunk.id}] {chunk.text}" for chunk in rag_context.chunks)
        graph_notes = "\n".join(str(item) for item in graph_context.relations)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a clinical support research assistant. Do not diagnose, prescribe, or validate delusional beliefs. "
                    "Ground clinical claims in provided evidence and cite chunk IDs when used."
                ),
            },
            {"role": "system", "content": f"Intent: {nlp_context.intent}\nEvidence:\n{evidence}\nGraph:\n{graph_notes}"},
            {"role": "user", "content": user_message},
        ]
        headers = {"Authorization": f"Bearer {self.settings.llm_api_key}"} if self.settings.llm_api_key else {}
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json={
                    "model": self.settings.llm_model or self.settings.model_id,
                    "messages": messages,
                    "temperature": 0.2,
                    "stream": False,
                },
            )
            response.raise_for_status()
            payload = response.json()
        text = payload["choices"][0]["message"]["content"]
        citations = [chunk.id for chunk in rag_context.chunks if f"[{chunk.id}]" in text] or format_citations(rag_context.chunks[:2])
        return ChatDraft(text=text, citations=citations, metadata={"provider": "openai_compatible"})

    def _stub_response(self, user_message: str, nlp_context: NlpContext, rag_context: RetrievalResult) -> ChatDraft:
        del user_message
        delusion_context = any(entity.label == "delusional_belief" for entity in nlp_context.entities)
        citation_chunks = rag_context.chunks
        if not delusion_context:
            citation_chunks = [chunk for chunk in citation_chunks if "delusion" not in chunk.source]
        citations = format_citations(citation_chunks[:2] or rag_context.chunks[:2])
        citation_text = " ".join(f"[{citation}]" for citation in citations)
        if nlp_context.language == "pl":
            if delusion_context:
                text = (
                    "Brzmi to bardzo przerażająco i rozumiem, że możesz czuć się zagrożony. "
                    "Nie będę zakładać, że ta interpretacja jest prawdziwa bez dowodów. "
                    "Spróbujmy oddzielić samo uczucie zagrożenia od tego, co można potwierdzić: kiedy to się zaczęło, "
                    "czy są momenty, gdy to słabnie, i czy ktoś zaufany może pomóc Ci ocenić sytuację z zewnątrz. "
                    f"{citation_text}"
                )
            else:
                text = (
                    "To, co opisujesz, może być ważnym sygnałem klinicznym, ale nie jest diagnozą. "
                    "Warto zebrać więcej informacji o czasie trwania, nasileniu, śnie, nastroju, używkach i bezpieczeństwie. "
                    "Mogę podać ogólne informacje psychoedukacyjne i pytania do omówienia ze specjalistą, ale nie zastąpię diagnozy ani planu leczenia. "
                    f"{citation_text}"
                )
        else:
            text = (
                "What you describe may be clinically relevant, but it is not a diagnosis. "
                "It would be important to understand duration, severity, sleep, mood, substances, and immediate safety. "
                "I can offer general psychoeducation and questions to discuss with a qualified professional, not a diagnosis or treatment plan. "
                f"{citation_text}"
            )
        return ChatDraft(text=text.strip(), citations=citations, metadata={"provider": "stub"})
