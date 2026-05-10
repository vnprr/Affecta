from clinical_rag_agent.nlp.contradiction_detector import ContradictionDetector
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import ConversationTurn, PatientSession
from clinical_rag_agent.schemas.rag import RetrievalResult


def test_contradiction_detection_catches_patient_context_mismatch():
    session = PatientSession(
        session_id="s1",
        turns=[ConversationTurn(user_message="Nie mam myśli samobójczych.", assistant_message="Rozumiem.")],
    )
    draft = ChatDraft(text="Ponieważ masz myśli samobójcze, musimy założyć wysokie ryzyko.")

    report = ContradictionDetector().check(draft, session, RetrievalResult(query=""))

    assert report.contradictions
    assert report.contradictions[0].severity == "high"

