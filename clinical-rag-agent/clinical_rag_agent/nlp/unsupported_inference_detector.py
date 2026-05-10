import re
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import PatientSession
from clinical_rag_agent.schemas.hallucination import UnsupportedInferenceReport


class UnsupportedInferenceDetector:
    FIELDS = {
        "trauma_history": re.compile(r"(w dzieciństwie doświadczałeś przemocy|childhood abuse|trauma history)", re.I),
        "substance_use": re.compile(r"(nadużywasz alkoholu|używasz narkotyków|substance abuse)", re.I),
        "family_history": re.compile(r"(w twojej rodzinie występowała|family history of)", re.I),
    }

    def check(self, draft: ChatDraft, session: PatientSession) -> UnsupportedInferenceReport:
        history = session.conversation_text().lower()
        inferences: list[str] = []
        for field, pattern in self.FIELDS.items():
            if pattern.search(draft.text) and field.replace("_", " ") not in history:
                inferences.append(field)
        return UnsupportedInferenceReport(inferences=inferences)

