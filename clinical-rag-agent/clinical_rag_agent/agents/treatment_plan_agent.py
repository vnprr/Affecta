from clinical_rag_agent.agents.base_agent import BaseAgent


class TreatmentPlanAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="treatment_plan_agent", goal="Provide psychoeducation and clinician-facing questions, not prescriptions.")

