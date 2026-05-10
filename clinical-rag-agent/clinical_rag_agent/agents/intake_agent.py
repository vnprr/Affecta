from clinical_rag_agent.agents.base_agent import BaseAgent


class IntakeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="intake_agent", goal="Collect initial context without diagnosing.")

