from clinical_rag_agent.agents.base_agent import BaseAgent
from clinical_rag_agent.schemas.therapy import CaseFormulation, TherapeuticCaseState
from clinical_rag_agent.services.therapy_plan_service import TherapyPlanService


class TreatmentPlanAgent(BaseAgent):
    """Builds a therapeutic work plan (goals, focus, psychoeducation), not prescriptions."""

    def __init__(self, therapy_plan_service: TherapyPlanService):
        super().__init__(
            name="treatment_plan_agent",
            goal="Provide psychoeducation and clinician-facing questions, not prescriptions.",
        )
        self.therapy_plan_service = therapy_plan_service

    def update_plan(
        self,
        state: TherapeuticCaseState,
        formulation: CaseFormulation,
    ) -> TherapeuticCaseState:
        return self.therapy_plan_service.update(state, formulation)
