from clinical_rag_agent.schemas.clinical import NlpContext
from clinical_rag_agent.schemas.therapy import (
    TherapeuticCaseState,
    TherapeuticHypothesis,
)
from clinical_rag_agent.services.case_formulation_service import CaseFormulationService
from clinical_rag_agent.services.hypothesis_service import HypothesisService
from clinical_rag_agent.services.intake_service import IntakeService
from clinical_rag_agent.services.therapy_plan_service import TherapyPlanService


def _state_with_patterns(**kwargs) -> TherapeuticCaseState:
    return TherapeuticCaseState(session_id="s1", **kwargs)


def test_case_formulation_consolidates_patterns():
    state = _state_with_patterns(
        recurring_patterns=["fear of abandonment", "reassurance seeking"],
        relational_patterns=["fear of abandonment"],
        cognitive_patterns=["catastrophic interpretation"],
        behavioral_patterns=["avoidance"],
    )
    formulation = CaseFormulationService().build(state)

    assert "fear of abandonment" in formulation.triggers
    assert "reassurance seeking" in formulation.coping_strategies
    # The most-repeated pattern should rank first among dominant themes.
    assert formulation.dominant_themes[0] == "fear of abandonment"


def test_hypothesis_service_creates_low_confidence_internal_hypothesis():
    state = _state_with_patterns(recurring_patterns=["fear of abandonment"])
    formulation = CaseFormulationService().build(state)

    HypothesisService().update(state, formulation, evidence_excerpt="I keep checking my phone")

    labels = {h.label for h in state.working_hypotheses}
    assert "attachment_anxiety" in labels
    attachment = next(h for h in state.working_hypotheses if h.label == "attachment_anxiety")
    assert attachment.confidence == "low"
    assert attachment.status == "new"
    assert attachment.implications_for_session  # guidance present


def test_hypothesis_service_flags_borderline_traits_only_with_enough_signals():
    state = _state_with_patterns(
        recurring_patterns=[
            "fear of abandonment",
            "anger after hurt",
            "relational pursuit/withdrawal",
            "self-criticism",
        ]
    )
    formulation = CaseFormulationService().build(state)
    HypothesisService().update(state, formulation)

    labels = {h.label for h in state.working_hypotheses}
    assert "borderline_traits_possible" in labels
    borderline = next(h for h in state.working_hypotheses if h.label == "borderline_traits_possible")
    # Cautious by default — never auto-high, never visible status.
    assert borderline.confidence in {"low", "medium"}
    assert borderline.status not in {"confirmed_by_human"}


def test_hypothesis_service_respects_human_rejection():
    state = _state_with_patterns(recurring_patterns=["fear of abandonment"])
    state.working_hypotheses.append(
        TherapeuticHypothesis(
            id="hyp_attachment_anxiety",
            label="attachment_anxiety",
            description="x",
            confidence="low",
            status="rejected_by_human",
        )
    )
    formulation = CaseFormulationService().build(state)
    HypothesisService().update(state, formulation, evidence_excerpt="more evidence")

    rejected = next(h for h in state.working_hypotheses if h.label == "attachment_anxiety")
    assert rejected.status == "rejected_by_human"
    assert rejected.evidence_from_conversation == []  # untouched


def test_therapy_plan_creates_visible_and_internal_goals():
    state = _state_with_patterns(
        recurring_patterns=["catastrophic interpretation", "emotional shutdown"]
    )
    formulation = CaseFormulationService().build(state)
    TherapyPlanService().update(state, formulation)

    visible = [g for g in state.therapy_goals if g.visibility == "visible"]
    internal = [g for g in state.therapy_goals if g.visibility == "internal"]
    assert any(g.suggested_method == "CBT" for g in visible)
    assert internal  # emotional shutdown -> internal DBT goal
    assert state.psychoeducation_topics  # populated


def test_therapy_plan_respects_human_override_focus():
    state = _state_with_patterns(recurring_patterns=["catastrophic interpretation"])
    state.human_override_focus = "self-worth"
    formulation = CaseFormulationService().build(state)
    TherapyPlanService().update(state, formulation)

    assert state.active_focus == "self-worth"


def test_intake_service_seeds_problem_and_tracks_missing_context():
    state = TherapeuticCaseState(session_id="s1", current_stage="intake")
    IntakeService().enrich(
        state,
        "I have been feeling anxious",
        NlpContext(retrieval_query="anxious"),
    )

    assert state.presenting_problems
    assert state.missing_context  # most context still unknown
    assert state.intake_complete is False


def test_intake_service_noop_outside_intake_stage():
    state = TherapeuticCaseState(session_id="s1", current_stage="ongoing_work")
    IntakeService().enrich(state, "anything", None)

    assert state.presenting_problems == []
