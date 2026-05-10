from clinical_rag_agent.agents.base_agent import BaseAgent
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import PatientSession, RiskAssessment
from clinical_rag_agent.schemas.hallucination import HallucinationReport
from clinical_rag_agent.schemas.judge import JudgeReport


class JudgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="judge_agent", goal="Final safety gate after deterministic validators.")

    async def evaluate(
        self,
        draft: ChatDraft,
        session: PatientSession,
        risk: RiskAssessment,
        hallucination_report: HallucinationReport,
    ) -> JudgeReport:
        del draft, session
        reasons: list[str] = []
        if risk.level == "high":
            reasons.append("High risk must use crisis protocol.")
            return JudgeReport(approved=False, reasons=reasons, recommended_action="crisis_protocol")
        if not hallucination_report.approved:
            reasons.append(f"Hallucination report recommends {hallucination_report.recommended_action}.")
            return JudgeReport(approved=False, reasons=reasons, recommended_action=hallucination_report.recommended_action)
        return JudgeReport(approved=True, reasons=["Approved by deterministic MVP judge."], recommended_action="approve")

