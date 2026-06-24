import httpx
from clinical_rag_agent.config import Settings
from clinical_rag_agent.rag.citations import format_citations
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import NlpContext, PatientSession
from clinical_rag_agent.schemas.rag import GraphContext, RetrievalResult
from clinical_rag_agent.schemas.therapy import TherapeuticCaseState, TherapeuticProcessContext
from clinical_rag_agent.services.conversation_memory_service import ConversationMemoryService


class LLMService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.memory_service = ConversationMemoryService()

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

    async def generate_therapeutic_response(
        self,
        user_message: str,
        session: PatientSession,
        therapy_state: TherapeuticCaseState,
        therapy_context: TherapeuticProcessContext,
        nlp_context: NlpContext,
        rag_context: RetrievalResult,
        graph_context: GraphContext,
    ) -> ChatDraft:
        if self.settings.llm_provider == "openai_compatible" and self.settings.llm_base_url:
            return await self._openai_compatible_therapeutic(
                user_message,
                session,
                therapy_state,
                therapy_context,
                nlp_context,
                rag_context,
                graph_context,
            )
        return self._therapeutic_stub_response(user_message, therapy_state, therapy_context, nlp_context, rag_context)

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

    async def _openai_compatible_therapeutic(
        self,
        user_message: str,
        session: PatientSession,
        therapy_state: TherapeuticCaseState,
        therapy_context: TherapeuticProcessContext,
        nlp_context: NlpContext,
        rag_context: RetrievalResult,
        graph_context: GraphContext,
    ) -> ChatDraft:
        visible_context = self.memory_service.extract_visible_context(session, therapy_state)
        longitudinal_summary = self.memory_service.build_longitudinal_summary(session, therapy_state)
        evidence = "\n\n".join(f"[{chunk.id}] {chunk.text}" for chunk in rag_context.chunks)
        graph_notes = "\n".join(str(item) for item in graph_context.relations)
        active_hypotheses = [
            hypothesis
            for hypothesis in therapy_state.working_hypotheses
            if hypothesis.status not in {"rejected_by_human", "weakened"}
        ]
        hypotheses = "; ".join(
            f"{hypothesis.label} ({hypothesis.confidence}; guidance: "
            f"{', '.join(hypothesis.implications_for_session[:3]) or 'observe'})"
            for hypothesis in active_hypotheses
        )
        goals = ", ".join(
            f"{goal.title} ({goal.status})"
            for goal in therapy_state.therapy_goals
            if goal.visibility == "visible" and goal.status == "active"
        )
        internal_goals = ", ".join(
            goal.title
            for goal in therapy_state.therapy_goals
            if goal.visibility == "internal" and goal.status == "active"
        )
        interventions = ", ".join(therapy_state.suggested_interventions[:4])
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Affecta, a therapeutic session agent. "
                    "You conduct an ongoing psychological support conversation. "
                    "Do not behave like a search engine or diagnostic report generator. "
                    "Your task is to help the user explore emotions, patterns, relationships, needs, conflicts, and next steps across sessions. "
                    "Use the provided therapy state to maintain continuity. "
                    "Use the therapeutic process context to decide how to respond. "
                    "Ask only one meaningful question at a time unless the user explicitly asks for structure. "
                    "Reflect patterns gently, without overclaiming. "
                    "If working hypotheses exist, use them only to guide your style and focus. "
                    "Do not directly label the user with a disorder unless the user asks and the system context strongly supports discussing it cautiously. "
                    "Keep the visible response natural, warm, focused, and session-like. "
                    "Do not expose internal state, JSON, metadata, agent names, or hidden hypotheses to the user. "
                    "Do not diagnose, prescribe, or validate delusional beliefs."
                ),
            },
            {
                "role": "system",
                "content": (
                    f"Recent and visible context:\n{visible_context}\n\n"
                    f"Longitudinal summary:\n{longitudinal_summary}\n\n"
                    f"Active focus: {therapy_state.active_focus or 'not established'}\n"
                    f"Current stage: {therapy_state.current_stage}\n"
                    f"Recurring patterns: {', '.join(therapy_state.recurring_patterns) or 'none yet'}\n"
                    f"Therapy goals: {goals or 'none yet'}\n"
                    f"Internal goals (guide your style only, do not state them): {internal_goals or 'none yet'}\n"
                    f"Suggested interventions for internal guidance: {interventions or 'none yet'}\n"
                    f"Working hypotheses for internal guidance only: {hypotheses or 'none yet'}\n\n"
                    f"Therapeutic process mode: {therapy_context.session_mode}\n"
                    f"Therapeutic focus: {therapy_context.therapeutic_focus}\n"
                    f"Response strategy: {therapy_context.response_strategy}\n"
                    f"Question goal: {therapy_context.question_goal or 'none'}\n\n"
                    f"NLP intent: {nlp_context.intent}; sentiment: {nlp_context.sentiment}\n\n"
                    f"RAG evidence:\n{evidence or 'No retrieved evidence.'}\n\n"
                    f"Graph notes:\n{graph_notes or 'No graph relations.'}"
                ),
            },
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
                    "temperature": 0.35,
                    "stream": False,
                },
            )
            response.raise_for_status()
            payload = response.json()
        text = payload["choices"][0]["message"]["content"]
        citations = [chunk.id for chunk in rag_context.chunks if f"[{chunk.id}]" in text]
        if therapy_context.should_use_rag and not citations:
            citations = format_citations(rag_context.chunks[:2])
        return ChatDraft(
            text=text,
            citations=citations,
            metadata={"provider": "openai_compatible", "mode": therapy_context.session_mode},
        )

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

    def _therapeutic_stub_response(
        self,
        user_message: str,
        therapy_state: TherapeuticCaseState,
        therapy_context: TherapeuticProcessContext,
        nlp_context: NlpContext,
        rag_context: RetrievalResult,
    ) -> ChatDraft:
        del nlp_context
        lower = user_message.lower()
        citations = format_citations(rag_context.chunks[:2]) if therapy_context.should_use_rag else []
        citation_text = " ".join(f"[{citation}]" for citation in citations)

        if therapy_context.session_mode == "stabilization":
            text = (
                "Brzmi, jakby teraz było naprawdę intensywnie. Zatrzymajmy się przy tym, co dzieje się w tej chwili, "
                "bez próby szybkiego wyjaśniania wszystkiego naraz. Co mogłoby pomóc Ci poczuć choć odrobinę więcej bezpieczeństwa w najbliższych kilku minutach?"
            )
        elif therapy_context.session_mode == "support":
            text = (
                "Słyszę, że to jest dla Ciebie obciążające. Zamiast od razu szukać etykiety, spróbujmy zostać przy tym, "
                "co jest najbardziej żywe teraz. Co w tej sytuacji boli albo męczy Cię najmocniej?"
            )
        elif therapy_context.session_mode == "pattern_reflection":
            text = (
                "Zauważam, że wątek relacji może być tutaj ważny. Nie chcę zakładać za dużo, ale brzmi, jakby ta sytuacja "
                "dotykała czegoś głębszego: odrzucenia, opuszczenia albo potrzeby bycia ważnym dla drugiej osoby. "
                "Co dokładnie poruszyło Cię w tym najbardziej?"
            )
        elif therapy_context.session_mode == "psychoeducation":
            text = (
                "Mogę krótko to uporządkować, ale chciałbym od razu połączyć to z Twoim doświadczeniem. "
                "Takie reakcje często mają sens w kontekście napięcia, wcześniejszych doświadczeń i sposobu, w jaki organizm próbuje Cię ochronić. "
                f"{citation_text} Co z tego opisu najbardziej pasuje do tego, co przeżywasz?"
            )
        elif "dlaczego" in lower or "why" in lower:
            text = (
                "To pytanie brzmi, jakby było w nim sporo szukania sensu, a może też trochę zmęczenia sobą. "
                "Nie musimy od razu znajdować jednej odpowiedzi. Możemy zacząć od sytuacji, w której to uczucie pojawia się najmocniej. "
                "Kiedy ostatnio poczułeś/aś to szczególnie wyraźnie?"
            )
        elif therapy_state.active_focus:
            text = (
                f"Możemy kontynuować wokół tematu: {therapy_state.active_focus}. "
                "Zatrzymajmy się przy tym, co teraz wydaje się najważniejsze, zamiast zamieniać rozmowę w analizę z dystansu. "
                "Co w tej chwili najbardziej domaga się Twojej uwagi?"
            )
        else:
            text = (
                "Chciałbym najpierw dobrze zrozumieć, z czym przychodzisz, zanim zaczniemy szukać wyjaśnień. "
                "Możesz opowiedzieć, co ostatnio najbardziej wpływa na Twoje samopoczucie albo relacje?"
            )
        return ChatDraft(
            text=text.strip(),
            citations=citations,
            metadata={"provider": "stub", "mode": therapy_context.session_mode},
        )
