from clinical_rag_agent.agents.base_agent import BaseAgent
from clinical_rag_agent.rag.citations import format_citations
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import PatientSession
from clinical_rag_agent.schemas.hallucination import HallucinationReport
from clinical_rag_agent.schemas.judge import JudgeReport
from clinical_rag_agent.schemas.rag import RetrievalResult


class HallucinationGuardAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="hallucination_guard_agent", goal="Rewrite unsafe drafts into grounded, cautious responses.")

    async def rewrite(
        self,
        draft: ChatDraft,
        report: HallucinationReport,
        session: PatientSession,
        rag_context: RetrievalResult,
    ) -> ChatDraft:
        del draft, session
        citations = format_citations(rag_context.chunks[:2])
        citation_text = " ".join(f"[{citation}]" for citation in citations)
        if report.delusion_validation_detected:
            text = (
                "Brzmi to bardzo obciążająco i rozumiem, że może wywoływać silny lęk. "
                "Nie będę potwierdzać interpretacji, której nie możemy sprawdzić. "
                "Możemy natomiast oddzielić to, co czujesz, od tego, co da się potwierdzić, i zastanowić się, kto zaufany może pomóc Ci ocenić sytuację. "
                f"{citation_text}"
            )
        elif report.recommended_action == "force_human_review":
            text = (
                "Nie mam wystarczających podstaw, żeby bezpiecznie odpowiedzieć na to jako system automatyczny. "
                "Najbezpieczniej omówić tę sprawę z wykwalifikowanym specjalistą, szczególnie jeśli dotyczy diagnozy, leczenia albo ryzyka. "
                f"{citation_text}"
            )
        else:
            text = (
                "Nie mam wystarczających dowodów, żeby przedstawić to jako pewny wniosek. "
                "Mogę potraktować to jako hipotezę do dalszej rozmowy i oprzeć się tylko na informacjach, które podałeś/aś oraz na dostępnych źródłach. "
                "W przypadku decyzji diagnostycznych lub leczenia potrzebna jest ocena specjalisty. "
                f"{citation_text}"
            )
        return ChatDraft(text=text.strip(), citations=citations, metadata={"agent": self.name, "rewrite_reason": report.recommended_action})

    async def safe_fallback_response(self, user_message: str, judge_report: JudgeReport) -> ChatDraft:
        del user_message
        return ChatDraft(
            text=(
                "Nie mogę bezpiecznie wygenerować konkretnej odpowiedzi na podstawie dostępnych informacji. "
                "Najlepszym kolejnym krokiem jest rozmowa z wykwalifikowanym specjalistą lub doprecyzowanie, czego dokładnie dotyczy pytanie."
            ),
            citations=[],
            metadata={"agent": self.name, "judge": judge_report.model_dump()},
        )

