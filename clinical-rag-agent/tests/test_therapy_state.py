import pytest
from clinical_rag_agent.schemas.clinical import NlpContext, PatientSession
from clinical_rag_agent.schemas.therapy import TherapeuticCaseState, TherapeuticProcessContext
from clinical_rag_agent.services.therapeutic_process_service import TherapeuticProcessService
from clinical_rag_agent.services.therapy_state_service import TherapyStateService


@pytest.mark.asyncio
async def test_therapy_state_service_creates_state(tmp_path):
    service = TherapyStateService(tmp_path / "therapy_states")

    state = await service.get_or_create("session/with spaces")

    assert state.session_id == "session/with spaces"
    assert state.current_stage == "intake"
    assert (tmp_path / "therapy_states").exists()


@pytest.mark.asyncio
async def test_therapeutic_process_detects_relationship_pattern():
    context = await TherapeuticProcessService().analyze(
        user_message="My partner left me and I feel rejected.",
        session=PatientSession(session_id="s1"),
        therapy_state=TherapeuticCaseState(session_id="s1"),
        nlp_context=NlpContext(retrieval_query="partner left rejected"),
    )

    assert context.session_mode == "pattern_reflection"
    assert context.therapeutic_focus == "relationship pattern"


@pytest.mark.asyncio
async def test_therapy_state_update_persists_after_turn(tmp_path):
    service = TherapyStateService(tmp_path / "therapy_states")
    state = await service.get_or_create("s1")
    context = TherapeuticProcessContext(
        session_mode="pattern_reflection",
        therapeutic_focus="relationship pattern",
        response_strategy="reflect recurring relationship pattern gently",
        should_ask_question=True,
        question_goal="explore what this relationship moment brought up emotionally",
    )

    updated = await service.update_after_turn(
        state=state,
        user_message="My partner left me and I feel rejected.",
        assistant_message="That sounds painful. What did it bring up?",
        therapy_context=context,
        nlp_context=NlpContext(retrieval_query="partner left rejected"),
    )

    assert updated.session_count == 1
    assert updated.active_focus == "relationship pattern"
    assert "relationship pattern" in updated.recurring_patterns
    assert (tmp_path / "therapy_states" / "s1.json").exists()
