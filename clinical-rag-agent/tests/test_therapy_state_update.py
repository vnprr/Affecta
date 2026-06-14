import pytest

from clinical_rag_agent.schemas.therapy import TherapeuticCaseState, TherapyStateUpdate
from clinical_rag_agent.services.therapy_state_service import TherapyStateService


@pytest.mark.asyncio
async def test_apply_update_changes_focus_and_continuity_fields(tmp_path):
    service = TherapyStateService(tmp_path / "therapy_states")
    state = TherapeuticCaseState(
        session_id="s1",
        recurring_patterns=["fear of abandonment"],
        suggested_next_steps=["Track reassurance loop."],
    )
    update = TherapyStateUpdate(
        new_emotional_states=["fear"],
        new_patterns=["fear of abandonment", "reassurance seeking"],
        new_relational_patterns=["fear of abandonment"],
        new_cognitive_patterns=["catastrophic interpretation"],
        new_behavioral_patterns=["reassurance seeking"],
        updated_active_focus="trigger sequence before reassurance seeking",
        summary_note="User linked silence with fear and checking.",
        longitudinal_summary_addition="Relationship silence triggered fear and checking.",
        open_questions=["What appears first before checking?"],
        suggested_next_steps=["Track reassurance loop.", "Separate facts from feared interpretation."],
    )

    updated = await service.apply_update(state, update)

    assert updated.session_count == 1
    assert updated.current_stage == "intake"
    assert updated.active_focus == "trigger sequence before reassurance seeking"
    assert updated.recurring_patterns == ["fear of abandonment", "reassurance seeking"]
    assert updated.relational_patterns == ["fear of abandonment"]
    assert updated.cognitive_patterns == ["catastrophic interpretation"]
    assert updated.behavioral_patterns == ["reassurance seeking"]
    assert updated.last_session_summary == "User linked silence with fear and checking."
    assert updated.open_questions == ["What appears first before checking?"]
    assert updated.suggested_next_steps == [
        "Track reassurance loop.",
        "Separate facts from feared interpretation.",
    ]
    assert "Relationship silence triggered fear and checking." in updated.longitudinal_summary


@pytest.mark.asyncio
async def test_apply_update_limits_long_lists(tmp_path):
    service = TherapyStateService(tmp_path / "therapy_states")
    state = TherapeuticCaseState(
        session_id="s1",
        recurring_patterns=[f"pattern-{index}" for index in range(35)],
    )

    updated = await service.apply_update(state, TherapyStateUpdate(new_patterns=["new-pattern"]))

    assert len(updated.recurring_patterns) == 30
    assert updated.recurring_patterns[-1] == "new-pattern"
