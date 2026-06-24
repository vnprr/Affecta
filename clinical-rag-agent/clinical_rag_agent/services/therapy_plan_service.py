"""Rule-based therapy-plan engine.

Creates the longer-term direction of the work: explicit (visible) therapy goals,
internal goals that only guide the agent's style, the active focus, suggested
interventions and psychoeducation topics. This is a *therapeutic work plan*, not a
medical treatment plan: it never prescribes and never produces diagnoses.

Goal identity is derived from a slug of the title so that the same goal is updated
rather than duplicated across sessions. Goals/focus set by a human reviewer
(``human_override_focus``, goals with a non-active human status) are respected.
"""

from dataclasses import dataclass, field

from clinical_rag_agent.schemas.therapy import (
    CaseFormulation,
    TherapeuticCaseState,
    TherapyGoal,
)


@dataclass(frozen=True)
class GoalRule:
    trigger: str  # pattern label that activates this goal
    title: str
    description: str
    visibility: str  # "visible" or "internal"
    method: str
    interventions: tuple[str, ...] = field(default_factory=tuple)
    psychoeducation: tuple[str, ...] = field(default_factory=tuple)


class TherapyPlanService:
    GOAL_RULES: tuple[GoalRule, ...] = (
        GoalRule(
            trigger="fear of abandonment",
            title="Recognize abandonment triggers earlier",
            description="Notice the moment abandonment fear begins and what it attaches to.",
            visibility="visible",
            method="CBT",
            interventions=("trigger-sequence mapping", "uncertainty tolerance practice"),
            psychoeducation=("attachment and abandonment fear",),
        ),
        GoalRule(
            trigger="reassurance seeking",
            title="Understand and gently interrupt the reassurance-seeking loop",
            description="See how reassurance changes emotion short- and long-term.",
            visibility="visible",
            method="CBT",
            interventions=("behavioral experiment: delay reassurance",),
            psychoeducation=("the reassurance-seeking loop",),
        ),
        GoalRule(
            trigger="catastrophic interpretation",
            title="Notice and test catastrophic predictions",
            description="Separate feared interpretations from what is currently known.",
            visibility="visible",
            method="CBT",
            interventions=("cognitive restructuring", "evidence-for-and-against"),
            psychoeducation=("thinking traps / cognitive distortions",),
        ),
        GoalRule(
            trigger="self-criticism",
            title="Develop a more compassionate inner stance",
            description="Recognize the self-critical voice and respond to it differently.",
            visibility="visible",
            method="schema",
            interventions=("compassionate reframe",),
            psychoeducation=("self-criticism and the inner critic",),
        ),
        GoalRule(
            trigger="rumination",
            title="Reduce time spent in rumination loops",
            description="Notice rumination early and shift attention deliberately.",
            visibility="visible",
            method="ACT",
            interventions=("cognitive defusion", "attention-shifting practice"),
            psychoeducation=("rumination vs. problem-solving",),
        ),
        GoalRule(
            trigger="avoidance",
            title="Approach avoided situations gradually",
            description="Build a gentle, values-based ladder toward avoided situations.",
            visibility="visible",
            method="CBT",
            interventions=("graded exposure", "behavioral activation"),
            psychoeducation=("how avoidance maintains anxiety",),
        ),
        GoalRule(
            trigger="emotional shutdown",
            title="Build emotion regulation skills",
            description="Develop ways to stay present and regulate intense emotion.",
            visibility="internal",
            method="DBT",
            interventions=("grounding skills", "emotion naming"),
            psychoeducation=("the window of tolerance",),
        ),
        GoalRule(
            trigger="anger after hurt",
            title="Work with anger that follows hurt",
            description="Track how hurt turns into anger and what it protects.",
            visibility="internal",
            method="DBT",
            interventions=("emotion chain analysis",),
            psychoeducation=("anger as a secondary emotion",),
        ),
    )

    def update(self, state: TherapeuticCaseState, formulation: CaseFormulation) -> TherapeuticCaseState:
        active_patterns = self._active_patterns(state, formulation)
        existing = {goal.id: goal for goal in state.therapy_goals}

        for rule in self.GOAL_RULES:
            if rule.trigger not in active_patterns:
                continue
            goal_id = f"goal_{self._slug(rule.title)}"
            current = existing.get(goal_id)
            if current is None:
                state.therapy_goals.append(self._new_goal(goal_id, rule))
                existing[goal_id] = state.therapy_goals[-1]
            elif current.status == "active":
                self._add_evidence(current, rule.trigger)
            self._extend_unique(state.suggested_interventions, list(rule.interventions))
            self._extend_unique(state.psychoeducation_topics, list(rule.psychoeducation))

        self._update_focus(state, formulation)
        self._trim(state)
        return state

    def _active_patterns(self, state: TherapeuticCaseState, formulation: CaseFormulation) -> set[str]:
        patterns: set[str] = set()
        patterns.update(state.recurring_patterns)
        patterns.update(state.relational_patterns)
        patterns.update(state.cognitive_patterns)
        patterns.update(state.behavioral_patterns)
        patterns.update(formulation.dominant_themes)
        return patterns

    def _update_focus(self, state: TherapeuticCaseState, formulation: CaseFormulation) -> None:
        # A human reviewer's focus always wins.
        if state.human_override_focus:
            state.active_focus = state.human_override_focus
            return
        if not state.active_focus and formulation.dominant_themes:
            state.active_focus = formulation.dominant_themes[0]

    def _new_goal(self, goal_id: str, rule: GoalRule) -> TherapyGoal:
        return TherapyGoal(
            id=goal_id,
            title=rule.title,
            description=rule.description,
            status="active",
            visibility=rule.visibility,
            suggested_method=rule.method,
            evidence=[f"linked to pattern: {rule.trigger}"],
        )

    @staticmethod
    def _add_evidence(goal: TherapyGoal, trigger: str) -> None:
        entry = f"linked to pattern: {trigger}"
        if entry not in goal.evidence:
            goal.evidence.append(entry)

    @staticmethod
    def _slug(title: str) -> str:
        return "".join(char if char.isalnum() else "_" for char in title.lower()).strip("_")

    @staticmethod
    def _extend_unique(target: list[str], values: list[str]) -> None:
        existing = {item.lower() for item in target}
        for value in values:
            normalized = value.strip()
            if normalized and normalized.lower() not in existing:
                target.append(normalized)
                existing.add(normalized.lower())

    @staticmethod
    def _trim(state: TherapeuticCaseState, max_items: int = 20) -> None:
        for name in ("suggested_interventions", "psychoeducation_topics"):
            values = getattr(state, name)
            if len(values) > max_items:
                setattr(state, name, values[-max_items:])
