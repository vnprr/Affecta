import pytest

from clinical_rag_agent.schemas.therapy import TherapeuticCaseState, TherapeuticProcessContext
from clinical_rag_agent.services.post_session_analysis_service import PostSessionAnalysisService


def _context() -> TherapeuticProcessContext:
    return TherapeuticProcessContext(
        session_mode="pattern_reflection",
        therapeutic_focus="relationship pattern",
        response_strategy="validate emotion and ask about the trigger sequence",
        should_ask_question=True,
        question_goal="explore what happens before the checking impulse",
    )


@pytest.mark.asyncio
async def test_post_session_analysis_detects_relationship_abandonment():
    result = await PostSessionAnalysisService().analyze_turn(
        session_id="s1",
        user_message="My girlfriend ignored me and I panicked that she will leave.",
        assistant_response="That sounds frightening. Let's slow down the sequence.",
        therapy_state=TherapeuticCaseState(session_id="s1"),
        therapy_context=_context(),
    )

    assert "fear of abandonment" in result.session_note.detected_patterns
    assert "relationship insecurity" in result.session_note.key_themes
    assert result.therapy_state_update.new_relational_patterns == ["fear of abandonment"]


@pytest.mark.asyncio
async def test_post_session_analysis_detects_checking_behavior():
    result = await PostSessionAnalysisService().analyze_turn(
        session_id="s1",
        user_message="I keep checking my phone and texting when my partner does not reply.",
        assistant_response="Let's notice what happens before checking.",
        therapy_state=TherapeuticCaseState(session_id="s1"),
        therapy_context=_context(),
    )

    assert "reassurance seeking" in result.session_note.detected_patterns
    assert "checking behavior" in result.session_note.behavioral_material
    assert "trigger sequence before reassurance seeking" == result.session_note.suggested_next_focus


@pytest.mark.asyncio
async def test_post_session_analysis_detects_polish_emotional_keywords():
    result = await PostSessionAnalysisService().analyze_turn(
        session_id="s1",
        user_message="Czuję lęk, wstyd i bezsenność, kiedy ona nie odpisuje.",
        assistant_response="To brzmi jak dużo napięcia.",
        therapy_state=TherapeuticCaseState(session_id="s1"),
        therapy_context=_context(),
    )

    assert "fear" in result.session_note.key_emotions
    assert "shame" in result.session_note.key_emotions
    assert "sleep disturbance" in result.session_note.body_or_somatic_material


@pytest.mark.asyncio
async def test_post_session_analysis_copies_process_context():
    context = _context()

    result = await PostSessionAnalysisService().analyze_turn(
        session_id="s1",
        user_message="My partner left and I always think it ends this way.",
        assistant_response="Let's separate the fear from what we know.",
        therapy_state=TherapeuticCaseState(session_id="s1"),
        therapy_context=context,
    )

    assert result.session_note.session_mode == context.session_mode
    assert result.session_note.therapeutic_focus == context.therapeutic_focus
    assert result.session_note.response_strategy_used == context.response_strategy
    assert result.session_note.suggested_next_focus
