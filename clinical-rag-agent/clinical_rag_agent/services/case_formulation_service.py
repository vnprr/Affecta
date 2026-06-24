"""Build an evolving case formulation from the accumulated therapy state.

The formulation is the shared internal input for the hypothesis and therapy-plan
reasoning. It does not call the LLM: it consolidates and lightly classifies the
material that ``PostSessionAnalysisService`` and ``TherapyStateService`` have
already accumulated on the case state, so that the downstream services have one
coherent object to reason over.
"""

from clinical_rag_agent.schemas.therapy import CaseFormulation, TherapeuticCaseState


class CaseFormulationService:
    # Patterns that typically function as triggers / coping / protective material.
    TRIGGER_PATTERNS = {
        "fear of abandonment",
        "catastrophic interpretation",
        "anger after hurt",
    }
    COPING_PATTERNS = {
        "reassurance seeking",
        "avoidance",
        "emotional shutdown",
        "relational pursuit/withdrawal",
    }
    PROTECTIVE_MARKERS = (
        "support",
        "friend",
        "therapy",
        "help",
        "wsparcie",
        "przyjaci",
        "terapi",
        "pomoc",
    )

    def build(self, state: TherapeuticCaseState) -> CaseFormulation:
        all_patterns = self._unique(
            state.recurring_patterns
            + state.relational_patterns
            + state.cognitive_patterns
            + state.behavioral_patterns
        )
        triggers = [pattern for pattern in all_patterns if pattern in self.TRIGGER_PATTERNS]
        coping = [pattern for pattern in all_patterns if pattern in self.COPING_PATTERNS]
        protective = self._protective_factors(state)
        dominant = self._dominant_themes(state, all_patterns)
        return CaseFormulation(
            session_id=state.session_id,
            presenting_problems=list(state.presenting_problems),
            emotional_patterns=list(state.current_emotional_state),
            relational_patterns=list(state.relational_patterns),
            cognitive_patterns=list(state.cognitive_patterns),
            behavioral_patterns=list(state.behavioral_patterns),
            triggers=triggers,
            coping_strategies=coping,
            protective_factors=protective,
            dominant_themes=dominant,
        )

    def _protective_factors(self, state: TherapeuticCaseState) -> list[str]:
        haystack = " ".join(
            [state.longitudinal_summary or "", state.last_session_summary or ""]
        ).lower()
        factors: list[str] = []
        if any(marker in haystack for marker in self.PROTECTIVE_MARKERS):
            factors.append("reports access to some support or help-seeking")
        if state.therapy_goals:
            factors.append("engaged in goal-directed therapeutic work")
        return factors

    def _dominant_themes(self, state: TherapeuticCaseState, all_patterns: list[str]) -> list[str]:
        # Rank patterns by how often they recur across the accumulated lists.
        counts: dict[str, int] = {}
        for pattern in (
            state.recurring_patterns
            + state.relational_patterns
            + state.cognitive_patterns
            + state.behavioral_patterns
        ):
            counts[pattern] = counts.get(pattern, 0) + 1
        ranked = sorted(all_patterns, key=lambda pattern: counts.get(pattern, 0), reverse=True)
        return ranked[:5]

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            normalized = value.strip()
            key = normalized.lower()
            if normalized and key not in seen:
                seen.add(key)
                result.append(normalized)
        return result
