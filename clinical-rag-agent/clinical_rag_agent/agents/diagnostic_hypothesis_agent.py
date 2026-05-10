from clinical_rag_agent.agents.base_agent import BaseAgent


class DiagnosticHypothesisAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="diagnostic_hypothesis_agent", goal="Frame possibilities as hypotheses, never diagnoses.")

