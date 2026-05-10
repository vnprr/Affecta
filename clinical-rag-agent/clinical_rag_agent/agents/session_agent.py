from clinical_rag_agent.agents.base_agent import BaseAgent


class SessionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="session_agent", goal="Maintain session continuity and context.")

