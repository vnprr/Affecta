from clinical_rag_agent.nlp.delusion_language_detector import DelusionLanguageDetector
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import ConversationTurn, PatientSession


def test_delusion_validation_detector_flags_validation():
    session = PatientSession(
        session_id="s1",
        turns=[ConversationTurn(user_message="Wiem, że sąsiedzi przez ścianę sterują moimi myślami.", assistant_message="")],
    )
    draft = ChatDraft(text="To możliwe, że doświadczasz zewnętrznej kontroli myśli.")

    report = DelusionLanguageDetector().check(draft, session)

    assert report.detected is True

