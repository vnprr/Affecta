"""Rule-based working-hypothesis engine.

Turns the case formulation into careful, *internal* working hypotheses that guide
session style and direction. Hypotheses are never exposed to the user directly
(the therapeutic prompt only uses them for guidance). Confidence starts low and
can rise to ``medium`` automatically as evidence accumulates; ``high`` is reserved
for human confirmation. Hypotheses confirmed or rejected by a human reviewer are
never overwritten by the automatic rules.
"""

from dataclasses import dataclass, field

from clinical_rag_agent.schemas.therapy import (
    CaseFormulation,
    TherapeuticCaseState,
    TherapeuticHypothesis,
)


@dataclass(frozen=True)
class HypothesisRule:
    label: str
    description: str
    # Patterns/emotions that count as evidence for this hypothesis.
    triggers: frozenset[str]
    # Minimum distinct triggers that must be present to suggest the hypothesis.
    min_matches: int
    implications: tuple[str, ...]
    suggested_method: str


class HypothesisService:
    # Human-set statuses must never be overwritten by the automatic rules.
    PROTECTED_STATUSES = {"confirmed_by_human", "rejected_by_human"}

    RULES: tuple[HypothesisRule, ...] = (
        HypothesisRule(
            label="attachment_anxiety",
            description=(
                "Possible anxious attachment: heightened fear of abandonment with "
                "reassurance-seeking and distress when a close other feels distant."
            ),
            triggers=frozenset(
                {"fear of abandonment", "reassurance seeking", "relational pursuit/withdrawal"}
            ),
            min_matches=1,
            implications=(
                "track abandonment triggers",
                "work on tolerating uncertainty",
                "focus on emotion regulation before interpretation",
            ),
            suggested_method="CBT",
        ),
        HypothesisRule(
            label="emotional_dysregulation",
            description=(
                "Possible difficulty regulating intense emotions, with rapid shifts "
                "between states and shutdown when overwhelmed."
            ),
            triggers=frozenset(
                {"anger after hurt", "emotional shutdown", "shame spiral", "fear of abandonment"}
            ),
            min_matches=2,
            implications=(
                "validate emotional intensity",
                "introduce emotion naming and grounding",
                "avoid premature interpretation during high arousal",
            ),
            suggested_method="DBT",
        ),
        HypothesisRule(
            label="borderline_traits_possible",
            description=(
                "Cautious, low-confidence observation of borderline-like traits: "
                "abandonment fear, relational instability, rapid emotional shifts and "
                "self-criticism. Internal guidance only; not a diagnosis."
            ),
            triggers=frozenset(
                {
                    "fear of abandonment",
                    "anger after hurt",
                    "relational pursuit/withdrawal",
                    "emotional shutdown",
                    "shame spiral",
                    "self-criticism",
                }
            ),
            min_matches=3,
            implications=(
                "use more validation",
                "track emotional intensity and relational swings",
                "focus on emotion regulation and distress tolerance",
                "avoid premature labeling or confrontation",
            ),
            suggested_method="DBT",
        ),
        HypothesisRule(
            label="depressive_patterns",
            description="Possible depressive process: low mood, withdrawal, hopelessness or anhedonia.",
            triggers=frozenset({"avoidance", "emotional shutdown", "self-criticism"}),
            min_matches=2,
            implications=(
                "monitor mood and activation",
                "consider behavioral activation",
                "watch for hopelessness and safety",
            ),
            suggested_method="CBT",
        ),
        HypothesisRule(
            label="anxiety_patterns",
            description="Possible anxiety process: catastrophic prediction, worry loops and avoidance.",
            triggers=frozenset({"catastrophic interpretation", "rumination", "avoidance"}),
            min_matches=2,
            implications=(
                "test catastrophic predictions",
                "support gradual approach to avoided situations",
                "work with worry and uncertainty",
            ),
            suggested_method="CBT",
        ),
        HypothesisRule(
            label="self_criticism_shame",
            description="Prominent self-criticism and shame shaping the user's inner stance.",
            triggers=frozenset({"self-criticism", "shame spiral"}),
            min_matches=1,
            implications=(
                "notice the self-critical voice",
                "build a more compassionate inner stance",
                "separate behavior from global self-judgment",
            ),
            suggested_method="schema",
        ),
    )

    def update(
        self,
        state: TherapeuticCaseState,
        formulation: CaseFormulation,
        evidence_excerpt: str | None = None,
    ) -> TherapeuticCaseState:
        present = self._present_signals(state, formulation)
        existing = {hypothesis.label: hypothesis for hypothesis in state.working_hypotheses}

        for rule in self.RULES:
            matched = sorted(present & rule.triggers)
            if len(matched) < rule.min_matches:
                continue
            current = existing.get(rule.label)
            if current is None:
                state.working_hypotheses.append(
                    self._new_hypothesis(rule, matched, evidence_excerpt)
                )
            elif current.status not in self.PROTECTED_STATUSES:
                self._reinforce(current, matched, evidence_excerpt)
        return state

    def _present_signals(
        self, state: TherapeuticCaseState, formulation: CaseFormulation
    ) -> set[str]:
        signals: set[str] = set()
        signals.update(state.recurring_patterns)
        signals.update(state.relational_patterns)
        signals.update(state.cognitive_patterns)
        signals.update(state.behavioral_patterns)
        signals.update(formulation.dominant_themes)
        return signals

    def _new_hypothesis(
        self, rule: HypothesisRule, matched: list[str], evidence_excerpt: str | None
    ) -> TherapeuticHypothesis:
        evidence = [f"observed: {marker}" for marker in matched]
        if evidence_excerpt:
            evidence.append(evidence_excerpt)
        return TherapeuticHypothesis(
            id=f"hyp_{rule.label}",
            label=rule.label,
            description=rule.description,
            confidence="low",
            evidence_from_conversation=evidence,
            status="new",
            implications_for_session=list(rule.implications),
        )

    def _reinforce(
        self,
        hypothesis: TherapeuticHypothesis,
        matched: list[str],
        evidence_excerpt: str | None,
    ) -> None:
        for marker in matched:
            entry = f"observed: {marker}"
            if entry not in hypothesis.evidence_from_conversation:
                hypothesis.evidence_from_conversation.append(entry)
        if evidence_excerpt and evidence_excerpt not in hypothesis.evidence_from_conversation:
            hypothesis.evidence_from_conversation.append(evidence_excerpt)

        evidence_count = len(hypothesis.evidence_from_conversation)
        # Status progression as evidence accumulates.
        if hypothesis.status == "new" and evidence_count >= 2:
            hypothesis.status = "observed"
        if hypothesis.status == "observed" and evidence_count >= 4:
            hypothesis.status = "strengthening"
        # Confidence rises to medium with accumulated evidence; high needs a human.
        if hypothesis.confidence == "low" and evidence_count >= 4:
            hypothesis.confidence = "medium"
