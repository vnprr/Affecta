from clinical_rag_agent.agents.base_agent import BaseAgent
from clinical_rag_agent.schemas.therapy import CaseFormulation, TherapeuticCaseState
from clinical_rag_agent.services.hypothesis_service import HypothesisService


class DiagnosticHypothesisAgent(BaseAgent):
    """Frames possibilities as careful, internal hypotheses, never diagnoses."""

    def __init__(self, hypothesis_service: HypothesisService):
        super().__init__(
            name="diagnostic_hypothesis_agent",
            goal="Frame possibilities as hypotheses, never diagnoses.",
        )
        self.hypothesis_service = hypothesis_service

    def update_hypotheses(
        self,
        state: TherapeuticCaseState,
        formulation: CaseFormulation,
        evidence_excerpt: str | None = None,
    ) -> TherapeuticCaseState:
        return self.hypothesis_service.update(state, formulation, evidence_excerpt)
