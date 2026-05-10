from clinical_rag_agent.agents.base_agent import BaseAgent
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import PatientSession, RiskAssessment


class CrisisAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="crisis_agent", goal="Prioritize immediate safety when high-risk signals appear.")

    async def respond(self, user_message: str, session: PatientSession, risk: RiskAssessment) -> ChatDraft:
        del user_message, session
        text = (
            "Widzę sygnały, że bezpieczeństwo może być teraz najważniejsze. "
            "Jeśli grozi Ci bezpośrednie niebezpieczeństwo albo możesz zrobić sobie krzywdę, zadzwoń pod lokalny numer alarmowy "
            "lub jedź na najbliższy SOR. Jeśli możesz, skontaktuj się teraz z zaufaną osobą i nie zostawaj sam/a. "
            "Nie będę prowadzić dalszej analizy klinicznej, dopóki nie zadbamy o natychmiastowe bezpieczeństwo."
        )
        return ChatDraft(text=text, citations=[], metadata={"agent": self.name, "risk": risk.model_dump()})

