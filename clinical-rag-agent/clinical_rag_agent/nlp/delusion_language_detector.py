import re
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import PatientSession
from clinical_rag_agent.schemas.hallucination import DelusionReport


class DelusionLanguageDetector:
    BELIEF_MARKERS = re.compile(r"(śledz|kontrol|steruj|podsłuch|control.+thought|watching|following)", re.I)
    VALIDATING = re.compile(
        r"(masz rację|to możliwe, że|brzmi jak kontrola myśli|to może być dowód|you are right|it is possible they|proof that)",
        re.I,
    )
    SAFE_MARKERS = re.compile(r"(nie będę zakładać|bez dowodów|oddzielić|możemy potwierdzić|without evidence|what we can verify)", re.I)

    def check(self, draft: ChatDraft, session: PatientSession) -> DelusionReport:
        context = f"{session.conversation_text()}\n{draft.text}"
        if self.BELIEF_MARKERS.search(context) and self.VALIDATING.search(draft.text) and not self.SAFE_MARKERS.search(draft.text):
            return DelusionReport(detected=True, problems=["Assistant appears to validate an unverified delusional belief."])
        return DelusionReport(detected=False)

