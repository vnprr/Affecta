import re
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import PatientSession
from clinical_rag_agent.schemas.hallucination import Contradiction, ContradictionReport
from clinical_rag_agent.schemas.rag import RetrievalResult


class ContradictionDetector:
    NEGATED_SUICIDE = re.compile(r"(nie mam|nie miewam|brak|no)\s+(myśli samobójczych|samobój|suicidal thoughts)", re.I)
    ASSERTED_SUICIDE = re.compile(r"(masz|miewasz|you have|because you have).{0,40}(myśli samobójc|suicidal thoughts)", re.I)

    def check(self, draft: ChatDraft, session: PatientSession, rag_context: RetrievalResult) -> ContradictionReport:
        history = session.conversation_text()
        contradictions: list[Contradiction] = []
        if self.NEGATED_SUICIDE.search(history) and self.ASSERTED_SUICIDE.search(draft.text):
            contradictions.append(
                Contradiction(
                    contradiction_type="patient_context_mismatch",
                    severity="high",
                    reason="Patient denied suicidal thoughts, but draft asserts them.",
                )
            )
        return ContradictionReport(contradictions=contradictions)

