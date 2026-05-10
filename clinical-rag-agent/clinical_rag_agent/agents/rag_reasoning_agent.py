from clinical_rag_agent.agents.base_agent import BaseAgent


class RagReasoningAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="rag_reasoning_agent", goal="Use retrieved evidence to ground clinical support.")

