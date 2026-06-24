from clinical_rag_agent.agents.base_agent import BaseAgent
from clinical_rag_agent.schemas.clinical import NlpContext
from clinical_rag_agent.schemas.therapy import TherapeuticCaseState
from clinical_rag_agent.services.intake_service import IntakeService


class IntakeAgent(BaseAgent):
    """Collects initial context during the intake stage without diagnosing."""

    def __init__(self, intake_service: IntakeService):
        super().__init__(name="intake_agent", goal="Collect initial context without diagnosing.")
        self.intake_service = intake_service

    def assess(
        self,
        state: TherapeuticCaseState,
        user_message: str,
        nlp_context: NlpContext | None = None,
    ) -> TherapeuticCaseState:
        return self.intake_service.enrich(state, user_message, nlp_context)
