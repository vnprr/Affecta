from clinical_rag_agent.agents.base_agent import BaseAgent


class DelusionDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="delusion_detection_agent", goal="Detect language that may validate unverified delusional beliefs.")

